"""
Agent service — conversation CRUD + thin shim that hands a turn off to the
new harness brain.

The old waterfall (keyword routers, trigger tuples, structural router
regex, hand-rolled agentic loop) is gone. The model decides what to do
each turn via the tool registry in ``harness/``.
"""
from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Awaitable, Callable

from fastapi import HTTPException, status
from qdrant_client.models import Distance, PointStruct, VectorParams
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.bucket import Bucket
from app.models.conversation import Conversation, ConversationChunk, Message
from app.models.file import File
from app.models.platform import TeamMember
from app.models.user import Profile
from app.qdrant_client import get_async_qdrant_client
from app.schemas.agent import BucketQueryResponse
from app.services.notifications import create_notification
from app.services.agent.harness import (
    AgentRunner,
    TurnInput,
    TurnOutput,
)
from app.services.agent.harness.contract import BucketFile
from app.services.agent.retrieval import (
    format_sources_section,
    get_conversation_file_scope,
    search_bucket_documents_with_file_coverage,
)
from app.services.agent.llm import generate_answer, infer_style_guidance
from app.services.outline import clean_section_outline
from app.services.embeddings.service import (
    embed_texts as embed_dense_texts,
    embedding_dimension,
    estimate_token_count,
    split_text_for_memory,
)


logger = logging.getLogger(__name__)

# Reused by the streaming endpoint.
StepEvent = dict[str, str]
StepCallback = Callable[[StepEvent], Awaitable[None]]


CONVERSATION_COLLECTION = "conversation_chunks"


# ─────────────────────────────────────────────────────────── result wrapper ──

@dataclass
class AgentTurnResult:
    conversation: Conversation
    user_message: Message
    assistant_message: Message
    sources: list[dict[str, object]]
    used_web_search: bool
    follow_up_required: bool
    action_required: bool = False
    action_type: str | None = None
    action_options: list[str] | None = None
    thinking_steps: list[str] | None = None
    thinking_step_events: list[StepEvent] | None = None
    plan: list[dict[str, object]] | None = None


# ─────────────────────────────────────────────────────────── CRUD operations ──

async def get_bucket_for_user(db: AsyncSession, user_id: str, bucket_id: str) -> Bucket:
    stmt = select(Bucket).where(Bucket.id == uuid.UUID(bucket_id), Bucket.user_id == uuid.UUID(user_id))
    result = await db.execute(stmt)
    bucket = result.scalar_one_or_none()
    if bucket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bucket not found.")
    return bucket


async def get_profile_for_user(db: AsyncSession, user_id: str) -> Profile | None:
    result = await db.execute(select(Profile).where(Profile.user_id == uuid.UUID(user_id)))
    return result.scalar_one_or_none()


async def get_conversation_for_user(
    db: AsyncSession,
    user_id: str,
    bucket_id: str,
    conversation_id: str,
    *,
    acting_team_member_id: str | None = None,
    can_read_others_threads: bool = True,
) -> Conversation:
    """Fetch a conversation visible to the caller.

    For owners (acting_team_member_id is None): match by Conversation.user_id == user_id.
    For members: match by Conversation.user_id == owner_user_id, and additionally
    require created_by_team_member_id == acting_team_member_id when the caller
    cannot read others' threads.
    """
    stmt = select(Conversation).where(
        Conversation.id == uuid.UUID(conversation_id),
        Conversation.bucket_id == uuid.UUID(bucket_id),
        Conversation.user_id == uuid.UUID(user_id),
    )
    if acting_team_member_id and not can_read_others_threads:
        stmt = stmt.where(
            Conversation.created_by_team_member_id == uuid.UUID(acting_team_member_id)
        )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")
    return conversation


async def list_conversations(
    db: AsyncSession,
    user_id: str,
    bucket_id: str,
    *,
    acting_team_member_id: str | None = None,
    can_read_others_threads: bool = True,
) -> list[Conversation]:
    await get_bucket_for_user(db, user_id, bucket_id)
    stmt = (
        select(Conversation)
        .where(
            Conversation.user_id == uuid.UUID(user_id),
            Conversation.bucket_id == uuid.UUID(bucket_id),
        )
        .order_by(Conversation.updated_at.desc())
    )
    if acting_team_member_id and not can_read_others_threads:
        stmt = stmt.where(
            Conversation.created_by_team_member_id == uuid.UUID(acting_team_member_id)
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_conversation(
    db: AsyncSession,
    user_id: str,
    bucket_id: str,
    *,
    title: str | None,
    web_search_mode: str,
    follow_up_mode: str | None,
    created_by_team_member_id: str | None = None,
) -> Conversation:
    await get_bucket_for_user(db, user_id, bucket_id)
    profile = await get_profile_for_user(db, user_id)

    conversation = Conversation(
        user_id=uuid.UUID(user_id),
        bucket_id=uuid.UUID(bucket_id),
        title=(title or "New Conversation").strip() or "New Conversation",
        web_search_mode=web_search_mode,
        follow_up_mode=follow_up_mode or (profile.follow_up_mode if profile else "all_at_once"),
        created_by_team_member_id=(
            uuid.UUID(created_by_team_member_id) if created_by_team_member_id else None
        ),
    )
    db.add(conversation)
    await create_notification(
        db,
        user_id,
        "success",
        "Conversation created",
        f'Conversation "{conversation.title}" was created in this bucket.',
    )
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def delete_messages_from(
    db: AsyncSession,
    user_id: str,
    bucket_id: str,
    conversation_id: str,
    message_id: str,
    *,
    acting_team_member_id: str | None = None,
    can_read_others_threads: bool = True,
) -> None:
    await get_conversation_for_user(
        db,
        user_id,
        bucket_id,
        conversation_id,
        acting_team_member_id=acting_team_member_id,
        can_read_others_threads=can_read_others_threads,
    )
    result = await db.execute(
        select(Message.created_at).where(
            Message.id == uuid.UUID(message_id),
            Message.conversation_id == uuid.UUID(conversation_id),
        )
    )
    created_at = result.scalar_one_or_none()
    if created_at is None:
        raise HTTPException(status_code=404, detail="Message not found.")
    await db.execute(
        delete(Message).where(
            Message.conversation_id == uuid.UUID(conversation_id),
            Message.created_at >= created_at,
        )
    )
    await db.commit()


async def delete_conversation(
    db: AsyncSession,
    user_id: str,
    bucket_id: str,
    conversation_id: str,
    *,
    acting_team_member_id: str | None = None,
    can_read_others_threads: bool = True,
) -> None:
    conversation = await get_conversation_for_user(
        db,
        user_id,
        bucket_id,
        conversation_id,
        acting_team_member_id=acting_team_member_id,
        can_read_others_threads=can_read_others_threads,
    )
    conversation_title = conversation.title
    await db.delete(conversation)
    await create_notification(
        db,
        user_id,
        "warning",
        "Conversation deleted",
        f'Conversation "{conversation_title}" was deleted.',
    )
    await db.commit()


async def rename_conversation(
    db: AsyncSession,
    user_id: str,
    bucket_id: str,
    conversation_id: str,
    title: str,
    *,
    acting_team_member_id: str | None = None,
    can_read_others_threads: bool = True,
) -> Conversation:
    conversation = await get_conversation_for_user(
        db,
        user_id,
        bucket_id,
        conversation_id,
        acting_team_member_id=acting_team_member_id,
        can_read_others_threads=can_read_others_threads,
    )
    conversation.title = title.strip() or conversation.title
    await create_notification(
        db,
        user_id,
        "info",
        "Conversation renamed",
        f'Conversation renamed to "{conversation.title}".',
    )
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def pin_conversation(
    db: AsyncSession,
    user_id: str,
    bucket_id: str,
    conversation_id: str,
    is_pinned: bool,
    *,
    acting_team_member_id: str | None = None,
    can_read_others_threads: bool = True,
) -> Conversation:
    conversation = await get_conversation_for_user(
        db,
        user_id,
        bucket_id,
        conversation_id,
        acting_team_member_id=acting_team_member_id,
        can_read_others_threads=can_read_others_threads,
    )
    conversation.is_pinned = is_pinned
    await create_notification(
        db,
        user_id,
        "info",
        "Conversation pinned" if is_pinned else "Conversation unpinned",
        f'Conversation "{conversation.title}" was {"pinned" if is_pinned else "unpinned"}.',
    )
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def list_conversation_messages(
    db: AsyncSession,
    user_id: str,
    bucket_id: str,
    conversation_id: str,
    *,
    acting_team_member_id: str | None = None,
    can_read_others_threads: bool = True,
) -> list[Message]:
    await get_conversation_for_user(
        db,
        user_id,
        bucket_id,
        conversation_id,
        acting_team_member_id=acting_team_member_id,
        can_read_others_threads=can_read_others_threads,
    )
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == uuid.UUID(conversation_id))
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())


# ─────────────────────────────────────────────────────── conversation memory ──

async def _ensure_conversation_collection() -> None:
    client = get_async_qdrant_client()
    try:
        await client.get_collection(CONVERSATION_COLLECTION)
    except Exception:
        await client.create_collection(
            collection_name=CONVERSATION_COLLECTION,
            vectors_config=VectorParams(size=embedding_dimension(), distance=Distance.COSINE),
        )


async def _persist_message_memory(
    db: AsyncSession,
    *,
    conversation: Conversation,
    message: Message,
) -> None:
    memory_parts = split_text_for_memory(f"{message.role.title()}: {message.content}")
    if not memory_parts:
        message.embedding_status = "failed"
        return

    try:
        from app.services.embeddings.text_embeddings import embed_texts as embed_hybrid_texts

        embedding_rows = await embed_hybrid_texts(memory_parts)
        vectors = [[float(value) for value in row["dense"]] for row in embedding_rows]
    except Exception:
        vectors = [[float(value) for value in vector] for vector in embed_dense_texts(memory_parts)]

    await _ensure_conversation_collection()
    client = get_async_qdrant_client()

    qdrant_points: list[PointStruct] = []
    rows: list[ConversationChunk] = []
    for index, (part, vector) in enumerate(zip(memory_parts, vectors)):
        row = ConversationChunk(
            conversation_id=conversation.id,
            message_id=message.id,
            bucket_id=conversation.bucket_id,
            user_id=conversation.user_id,
            role=message.role,
            content=part,
            chunk_index=index,
            token_count=estimate_token_count(part),
            status="pending",
        )
        db.add(row)
        await db.flush()
        rows.append(row)
        qdrant_points.append(
            PointStruct(
                id=str(row.id),
                vector=vector,
                payload={
                    "conversation_id": str(conversation.id),
                    "message_id": str(message.id),
                    "bucket_id": str(conversation.bucket_id),
                    "user_id": str(conversation.user_id),
                    "role": message.role,
                    "content": part,
                    "chunk_index": index,
                },
            )
        )

    try:
        await client.upsert(collection_name=CONVERSATION_COLLECTION, wait=True, points=qdrant_points)
        for row in rows:
            row.status = "embedded"
        message.embedding_status = "embedded"
    except Exception:
        for row in rows:
            row.status = "failed"
        message.embedding_status = "failed"


# ─────────────────────────────────────────────────────────── turn helpers ──

async def _recent_chat_history(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    *,
    exclude_message_id: uuid.UUID | None = None,
    max_messages: int = 12,
) -> list[dict[str, str]]:
    """Return recent messages as [{role, content, sender_name?}], oldest→newest.
    ``sender_name`` is the display name of the team member who sent a user
    message (absent for the workspace owner and for assistant messages). Strip
    appended Sources sections so the history stays compact."""
    query = (
        select(Message.id, Message.role, Message.content, TeamMember.display_name)
        .outerjoin(TeamMember, Message.sender_team_member_id == TeamMember.id)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(max_messages + 2)
    )
    result = await db.execute(query)
    rows = result.all()
    history: list[dict[str, str]] = []
    for mid, role, content, sender_name in rows:
        if exclude_message_id and mid == exclude_message_id:
            continue
        clean = content
        if role == "assistant":
            sep = "\n\n---\n"
            if sep in clean:
                clean = clean.split(sep, 1)[0].strip()
        if not clean:
            continue
        entry: dict[str, str] = {"role": role, "content": clean}
        if role == "user" and sender_name:
            entry["sender_name"] = sender_name
        history.append(entry)
    history.reverse()
    return history[-max_messages:]


async def _load_bucket_files(db: AsyncSession, bucket_id: uuid.UUID) -> list[BucketFile]:
    result = await db.execute(
        select(File.id, File.name, File.status, File.is_agent_written)
        .where(File.bucket_id == bucket_id)
        .order_by(File.created_at.desc())
    )
    return [
        BucketFile(
            file_id=row.id,
            name=row.name,
            status=row.status,
            is_agent_written=bool(row.is_agent_written),
        )
        for row in result.all()
    ]


async def _resolve_active_file(
    db: AsyncSession,
    *,
    conversation_id: uuid.UUID,
    bucket_id: uuid.UUID,
    exclude_message_id: uuid.UUID,
) -> uuid.UUID | None:
    """Pick the most recent file actually used in this conversation, if any."""
    result = await db.execute(
        select(Message.chunks_used)
        .where(
            Message.conversation_id == conversation_id,
            Message.id != exclude_message_id,
        )
        .order_by(Message.created_at.desc())
        .limit(8)
    )
    for (chunks_used,) in result.all():
        for item in chunks_used or []:
            if isinstance(item, dict) and item.get("kind") == "document":
                raw = item.get("file_id")
                if not raw:
                    continue
                try:
                    candidate = uuid.UUID(str(raw))
                except Exception:
                    continue
                exists = await db.execute(
                    select(File.id).where(
                        File.id == candidate,
                        File.bucket_id == bucket_id,
                        File.status == "ready",
                    )
                )
                if exists.scalar_one_or_none() is not None:
                    return candidate
    return None


async def _maybe_set_conversation_title(conversation: Conversation, first_user_message: str) -> None:
    if conversation.title != "New Conversation":
        return
    trimmed = first_user_message.strip().replace("\n", " ")
    conversation.title = (trimmed[:77] + "...") if len(trimmed) > 80 else trimmed


# ─────────────────────────────────────────────────────────────────── runner ──

_RUNNER_SINGLETON: AgentRunner | None = None


def _get_runner() -> AgentRunner:
    global _RUNNER_SINGLETON
    if _RUNNER_SINGLETON is None:
        _RUNNER_SINGLETON = AgentRunner()
    return _RUNNER_SINGLETON


async def run_conversation_turn(
    db: AsyncSession,
    *,
    user_id: str,
    bucket_id: str,
    conversation_id: str,
    content: str,
    web_search_override: bool | None = None,
    agentic_mode: bool | None = None,   # kept for API compat — harness always agentic
    on_step: StepCallback | None = None,
    acting_team_member_id: str | None = None,
    can_read_others_threads: bool = True,
) -> AgentTurnResult:
    """Run one turn through the harness brain."""

    conversation = await get_conversation_for_user(
        db,
        user_id,
        bucket_id,
        conversation_id,
        acting_team_member_id=acting_team_member_id,
        can_read_others_threads=can_read_others_threads,
    )
    profile = await get_profile_for_user(db, user_id)
    user_message_text = content.strip()
    logger.info("[USER] %.120s", user_message_text.replace("\n", " "))

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=user_message_text,
        token_count=estimate_token_count(user_message_text),
        embedding_status="pending",
        sender_team_member_id=(
            uuid.UUID(acting_team_member_id) if acting_team_member_id else None
        ),
    )
    db.add(user_message)
    await db.flush()

    # Build the turn input.
    bucket_files = await _load_bucket_files(db, conversation.bucket_id)
    history = await _recent_chat_history(db, conversation.id, exclude_message_id=user_message.id)
    # Who is sending this turn — a named team member, or the workspace owner.
    current_speaker: str | None = None
    if acting_team_member_id:
        current_speaker = await db.scalar(
            select(TeamMember.display_name).where(
                TeamMember.id == uuid.UUID(acting_team_member_id)
            )
        )
    active_file = await _resolve_active_file(
        db,
        conversation_id=conversation.id,
        bucket_id=conversation.bucket_id,
        exclude_message_id=user_message.id,
    )
    scope = await get_conversation_file_scope(db, conversation.id)

    # Enforce the thread file scope at the source: the agent must only see and be
    # able to open files it is allowed to use. None = full bucket; otherwise the
    # model's file list (and every file-targeted tool) is limited to `scope`,
    # and an empty scope hides every file. Without this, tools like read_file /
    # get_page resolve against the full bucket and bypass the filter.
    if scope is not None:
        allowed = set(scope)
        bucket_files = [f for f in bucket_files if f.file_id in allowed]
        if active_file is not None and active_file not in allowed:
            active_file = None

    turn = TurnInput(
        user_message=user_message_text,
        conversation_history=history,
        active_file=active_file,
        bucket_files=bucket_files,
        web_mode=conversation.web_search_mode,
        web_override=web_search_override,
        model=(profile.preferred_llm if profile else None) or settings.llm_provider,
        now=datetime.now(timezone.utc),
        bucket_id=conversation.bucket_id,
        conversation_id=conversation.id,
        user_id=conversation.user_id,
        scope_file_ids=scope,
        current_speaker=current_speaker,
    )

    # Run the brain.
    output = await _run_with_callback(turn, db, on_step)

    # Persist the assistant message + sources + plan + steps.
    assistant_message = Message(
        conversation_id=conversation.id,
        parent_message_id=user_message.id,
        role="assistant",
        content=output.assistant_message,
        token_count=estimate_token_count(output.assistant_message),
        chunks_used=output.chunks_used,
        embedding_status="pending",
        agent_plan=output.plan,
        agent_steps=output.steps,
    )
    db.add(assistant_message)
    await db.flush()

    await _persist_message_memory(db, conversation=conversation, message=user_message)
    await _persist_message_memory(db, conversation=conversation, message=assistant_message)
    await _maybe_set_conversation_title(conversation, user_message_text)

    if assistant_message.role == "assistant":
        await create_notification(
            db,
            user_id,
            "info",
            "New AI reply",
            f'AI replied in "{conversation.title}".',
        )

    await db.commit()
    await db.refresh(conversation)

    thinking_step_labels = [s.get("label", "") for s in output.steps]
    return AgentTurnResult(
        conversation=conversation,
        user_message=user_message,
        assistant_message=assistant_message,
        sources=output.sources,
        used_web_search=output.used_web,
        follow_up_required=False,
        action_required=output.action_required,
        action_type=output.action_type,
        action_options=output.action_options,
        thinking_steps=thinking_step_labels,
        thinking_step_events=output.steps,
        plan=output.plan,
    )


async def _run_with_callback(
    turn: TurnInput,
    db: AsyncSession,
    on_step: StepCallback | None,
) -> TurnOutput:
    """Adapter — the harness's neutral `on_event(payload)` is mapped to the
    endpoint's per-event SSE pumps (`step`, `plan_update`, `token`)."""
    if on_step is None:
        return await _get_runner().run(turn, db, on_event=None)

    async def on_event(payload: dict[str, object]) -> None:
        kind = payload.get("kind")
        if kind == "step":
            event = payload.get("event") or {}
            try:
                await on_step(event)  # type: ignore[arg-type]
            except Exception:
                logger.debug("on_step (step) failed", exc_info=True)
        elif kind == "plan_update":
            try:
                await on_step({"type": "plan_update", "plan": payload.get("plan") or []})  # type: ignore[arg-type]
            except Exception:
                logger.debug("on_step (plan_update) failed", exc_info=True)
        elif kind == "token":
            try:
                await on_step({"type": "token", "text": payload.get("text") or ""})  # type: ignore[arg-type]
            except Exception:
                logger.debug("on_step (token) failed", exc_info=True)

    return await _get_runner().run(turn, db, on_event=on_event)


# ───────────────────────────────────────────── alt: standalone bucket query ──
#
# Used by the /buckets/{id}/query endpoint (not the chat). Stays single-pass —
# no conversation context, no harness brain. Kept simple on purpose.

# Minimum "best chunk" score for query() to trust retrieval and let the LLM
# answer. Below this, retrieval is treated as a miss and query() says "not found"
# rather than risk the LLM inventing. Calibrated against live scores (in-domain
# hits peak >=~0.5; clearly off-domain queries peak <~0.34). Tune if needed.
_WEAK_RETRIEVAL_MIN_SCORE = 0.40

# Counting cue: "how many / number of / count of …" or "total <structural noun>".
_COUNT_TRIGGER_RE = re.compile(
    r"\bhow many\b|\bhow much\b|\b(?:number|count|tally|amount)\s+of\b|"
    r"\btotal\s+(?:number\s+of\s+)?(?:pages?|sections?|headings?|chapters?|images?|"
    r"pictures?|photos?|figures?|graphics?|visuals?|visual\s+elements?|"
    r"text[\s-]?blocks?|chunks?|files?|documents?|docs?|pdfs?)\b",
    re.I,
)

# ALLOW-LIST: only these STRUCTURAL nouns may be answered from exact metadata.
# Order here = the order metrics appear in a multi-count answer. Anything not on
# this list (languages, ingredients, products, claims, emails, addresses,
# testimonials, …) is SEMANTIC and must fall through to normal retrieval.
_COUNT_NOUNS: list[tuple[str, str]] = [
    ("files", r"\b(files?|documents?|docs?|pdfs?)\b"),
    ("pages", r"\bpages?\b"),
    ("sections", r"\b(sections?|headings?|chapters?)\b"),
    ("images", r"\b(images?|pictures?|photos?|figures?|graphics?)\b"),
    ("text_blocks", r"\btext[\s-]?blocks?\b"),
    ("total_visuals", r"\b(visuals?|visual\s+elements?)\b"),
    ("chunks", r"\bchunks?\b"),
]

# Human label for each metric (singular, plural).
_COUNT_LABELS = {
    "files": ("file", "files"),
    "pages": ("page", "pages"),
    "sections": ("section", "sections"),
    "images": ("image", "images"),
    "text_blocks": ("text block", "text blocks"),
    "total_visuals": ("total visual", "total visuals"),
    "chunks": ("chunk", "chunks"),
}


# Words that end the "counted nouns" span — anything after these is a container
# reference ("…in the document", "…are listed on the page"), not a counted noun.
_COUNT_BOUNDARY_RE = re.compile(
    r"\b(?:are|is|were|was|in|on|inside|within|across|listed|present|contained|"
    r"appear|appears|exist|exists|do|does|did|have|has|that|which|there)\b",
    re.I,
)


def _detect_count_intents(question: str) -> list[str]:
    """Return EVERY structural metric a count question asks for, in canonical
    order (may be several). Empty list = not a structural count question, so the
    caller falls through to normal retrieval.

    Only allow-listed STRUCTURAL nouns trigger this; semantic nouns (languages,
    ingredients, products, claims, emails, addresses, testimonials, …) never do.
    We only look at the span between the counting cue and the first boundary word,
    so a container reference ("how many images IN THE DOCUMENT") doesn't get
    misread as also asking for a document/file count.
    """
    q = (question or "").lower()
    cue = _COUNT_TRIGGER_RE.search(q)
    if not cue:
        return []
    span = q[cue.start():]
    boundary = _COUNT_BOUNDARY_RE.search(span)
    if boundary:
        span = span[: boundary.start()]
    return [kind for kind, pat in _COUNT_NOUNS if re.search(pat, span)]


async def _count_answer_from_metadata(
    db: AsyncSession, bucket_id: uuid.UUID, kinds: list[str], scope: set | None
) -> str | None:
    """Deterministic, exact answer for one or more count metrics, straight from
    authoritative data (File metadata + layout/chunk counts). Returns None if
    there are no ready files so the caller can fall back to normal retrieval."""
    stmt = select(File).where(File.bucket_id == bucket_id, File.status == "ready")
    files = (await db.execute(stmt)).scalars().all()
    if scope is not None:
        # scope may be empty (thread hidden every file) -> no files in scope.
        scope_set = set(scope)
        files = [f for f in files if f.id in scope_set]
    if not files:
        return None

    totals: dict[str, int] = {}
    for kind in kinds:
        if kind == "files":
            totals["files"] = len(files)
        elif kind == "pages":
            totals["pages"] = sum(int(f.page_count or 0) for f in files)
        elif kind == "images":
            totals["images"] = sum(int(f.image_count or 0) for f in files)
        elif kind == "sections":
            totals["sections"] = sum(
                len(clean_section_outline(f.section_outline or [])) for f in files
            )
        elif kind == "chunks":
            from sqlalchemy import func
            from app.models.chunk import Chunk
            totals["chunks"] = int(
                (await db.execute(
                    select(func.count()).select_from(Chunk).where(
                        Chunk.file_id.in_([f.id for f in files]),
                        Chunk.status == "embedded",
                    )
                )).scalar() or 0
            )
        elif kind in ("text_blocks", "total_visuals"):
            # Layout-derived — load once, reuse for both metrics if both asked.
            if "text_blocks" not in totals and "total_visuals" not in totals:
                from app.services.mcp.tools import fetch_visual_list
                tb = tv = 0
                for f in files:
                    vl = await fetch_visual_list(db, bucket_id, f.id, limit=1)
                    if vl:
                        tb += int(vl.get("text_block_count") or 0)
                        tv += int(vl.get("total_visuals") or 0)
                if "text_blocks" in kinds:
                    totals["text_blocks"] = tb
                if "total_visuals" in kinds:
                    totals["total_visuals"] = tv

    if not totals:
        return None

    # Render in canonical order.
    ordered = [k for k, _ in _COUNT_NOUNS if k in totals]
    n_files = totals.get("files", len(files))

    def _label(kind: str, n: int) -> str:
        sing, plur = _COUNT_LABELS[kind]
        return f"{n} {sing if n == 1 else plur}"

    if len(ordered) == 1:
        kind = ordered[0]
        n = totals[kind]
        if kind == "files":
            names = ", ".join(f.name for f in files)
            return f"There {'is' if n == 1 else 'are'} {_label('files', n)} in this bucket: {names}."
        scope_txt = files[0].name if len(files) == 1 else f"this bucket ({len(files)} files)"
        return f"{scope_txt} has {_label(kind, n)} (from authoritative metadata)."

    lines = "\n".join(f"- {_COUNT_LABELS[k][1].capitalize()}: {totals[k]}" for k in ordered)
    scope_txt = files[0].name if len(files) == 1 else f"this bucket ({len(files)} files)"
    return f"Exact counts for {scope_txt} (from authoritative metadata):\n{lines}"


async def answer_bucket_query(
    db: AsyncSession,
    *,
    user_id: str,
    bucket_id: str,
    question: str,
    conversation_id: str | None = None,
) -> BucketQueryResponse:
    await get_bucket_for_user(db, user_id, bucket_id)
    profile = await get_profile_for_user(db, user_id)

    scope = None
    if conversation_id:
        scope = await get_conversation_file_scope(db, uuid.UUID(conversation_id))

    # Count/structure questions ("how many images/pages/sections/files…", incl.
    # multi-count) must be answered from exact metadata, never semantic retrieval
    # which undercounts. Only structural nouns trigger this; semantic nouns
    # (languages, ingredients, products…) fall through to normal retrieval.
    count_kinds = _detect_count_intents(question)
    if count_kinds:
        exact = await _count_answer_from_metadata(db, uuid.UUID(bucket_id), count_kinds, scope)
        if exact:
            logger.info("[QUERY] count-guard answered %s from metadata", count_kinds)
            return BucketQueryResponse(
                answer=exact,
                sources=[],
                used_web_search=False,
                follow_up_required=False,
            )

    document_chunks = await search_bucket_documents_with_file_coverage(
        db, uuid.UUID(bucket_id), question, limit=5, allowed_file_ids=scope,
    )

    # Weak-retrieval guard: if nothing relevant came back, do NOT let the LLM
    # synthesize from thin chunks (that's where it invents). Scores are not
    # pre-sorted, so judge by the best (max) score across returned chunks.
    # Calibrated: in-domain hits score >= ~0.5; off-domain queries peak < ~0.34.
    best_score = max((c.score for c in document_chunks), default=0.0)
    if not document_chunks or best_score < _WEAK_RETRIEVAL_MIN_SCORE:
        logger.info("[QUERY] weak retrieval (best=%.3f) — returning not-found", best_score)
        return BucketQueryResponse(
            answer=(
                "I couldn't find anything in this bucket's documents that answers that. "
                "It may not be covered in the uploaded files — try rephrasing, or check "
                "the document directly."
            ),
            sources=[],
            used_web_search=False,
            follow_up_required=False,
        )

    answer_body = await generate_answer(
        question=question,
        preferred_llm=profile.preferred_llm if profile else None,
        style_guidance=infer_style_guidance(question, []),
        document_chunks=document_chunks,
        memory_chunks=[],
        web_results=[],
    )
    # Strip any USED: marker the LLM may still emit (legacy prompt path).
    from app.services.agent.llm import extract_used_marker
    answer_body, _, _ = extract_used_marker(answer_body)
    sources_block, source_payload = format_sources_section(document_chunks, [])
    return BucketQueryResponse(
        answer=f"{answer_body.strip()}\n\n---\n\n{sources_block}",
        sources=source_payload,
        used_web_search=False,
        follow_up_required=False,
    )
