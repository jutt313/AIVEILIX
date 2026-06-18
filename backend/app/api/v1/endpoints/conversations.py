import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_user_context
from app.database import get_db
from app.models.message_feedback import MessageFeedback
from app.schemas.agent import (
    AgentReplyResponse,
    ConversationCreateRequest,
    ConversationListResponse,
    ConversationResponse,
    DeleteConversationResponse,
    MessageCreateRequest,
    MessageFeedbackRequest,
    MessageFeedbackResponse,
    MessageListResponse,
)
from app.services.agent import (
    create_conversation as create_conversation_service,
    delete_conversation as delete_conversation_service,
    delete_messages_from as delete_messages_from_service,
    list_conversation_messages,
    list_conversations as list_conversations_service,
    pin_conversation as pin_conversation_service,
    rename_conversation as rename_conversation_service,
    run_conversation_turn,
)
from app.services.agent.llm import generate_short_title
from app.services.notifications import create_notification
from app.services.quota import enforce_chat_quota
from app.services.team.permissions import (
    UserContext,
    get_bucket_access,
)
from sqlalchemy import select
from app.models.platform import TeamMember
from app.models.user import Profile, User
from app.schemas.agent import MessageSender


class RenameConversationRequest(BaseModel):
    title: str


class PinConversationRequest(BaseModel):
    is_pinned: bool


class ScopeUpdateRequest(BaseModel):
    file_ids: list[str]
    # Whether the thread is filtered. None = infer from file_ids (legacy clients):
    #   scoped=False -> full bucket access (ignore file_ids)
    #   scoped=True  -> restricted to file_ids (empty list = see no files)
    scoped: bool | None = None


class AutoTitleRequest(BaseModel):
    message: str


router = APIRouter(prefix="/buckets", tags=["conversations"])


async def _resolve_thread_ctx(
    db: AsyncSession,
    ctx: UserContext,
    bucket_id: str,
    *,
    require: str | None = None,
) -> dict:
    """Resolve per-bucket caller context for thread actions.

    Bucket access alone means the member can view + create threads. The only
    visibility knob is `history_scope`: 'from_now' restricts the member to
    their own threads, 'all' lets them read owner's & others' threads too.

    Raises 403 if the member lacks access or `require` permission.
    """
    bucket_uuid = uuid.UUID(bucket_id)
    if not ctx.is_member:
        return {
            "owner_id": str(ctx.user_id),
            "team_member_id": None,
            "can_read_others_threads": True,
            "can_use_mcp": True,
        }

    access = await get_bucket_access(db, ctx.team_member_id, bucket_uuid)
    if not access:
        raise HTTPException(
            status_code=403, detail="You don't have access to this bucket."
        )
    if require and not getattr(access, require, False):
        raise HTTPException(
            status_code=403, detail=f"You don't have permission: {require}."
        )
    return {
        "owner_id": str(ctx.owner_user_id),
        "team_member_id": str(ctx.team_member_id),
        "can_read_others_threads": access.history_scope == "all",
        "can_use_mcp": bool(access.can_use_mcp),
    }


@router.get("/{bucket_id}/conversations/{conversation_id}/scope")
async def get_thread_scope(
    bucket_id: str,
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    from sqlalchemy import text
    from app.services.agent.service import get_conversation_for_user

    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    await get_conversation_for_user(
        db,
        tctx["owner_id"],
        bucket_id,
        conversation_id,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )
    cid = uuid.UUID(conversation_id)
    active = await db.scalar(
        text("SELECT file_scope_active FROM conversations WHERE id = :cid"),
        {"cid": cid},
    )
    result = await db.execute(
        text("SELECT file_id FROM conversation_file_scope WHERE conversation_id = :cid"),
        {"cid": cid},
    )
    file_ids = [str(row[0]) for row in result.fetchall()]
    return {"file_ids": file_ids, "scoped": bool(active)}


@router.put("/{bucket_id}/conversations/{conversation_id}/scope")
async def set_thread_scope(
    bucket_id: str,
    conversation_id: str,
    body: ScopeUpdateRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    from sqlalchemy import text
    from app.services.agent.service import get_conversation_for_user

    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    await get_conversation_for_user(
        db,
        tctx["owner_id"],
        bucket_id,
        conversation_id,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )
    conv_uuid = uuid.UUID(conversation_id)
    # scoped=None -> infer from file_ids (legacy): non-empty means filtered.
    active = body.scoped if body.scoped is not None else (len(body.file_ids) > 0)
    await db.execute(
        text("DELETE FROM conversation_file_scope WHERE conversation_id = :cid"),
        {"cid": conv_uuid},
    )
    saved: list[str] = []
    if active:
        for fid in body.file_ids:
            res = await db.execute(
                text(
                    "INSERT INTO conversation_file_scope (conversation_id, file_id) "
                    "SELECT :cid, :fid WHERE EXISTS ("
                    "  SELECT 1 FROM files WHERE id = :fid AND bucket_id = :bid"
                    ") ON CONFLICT DO NOTHING RETURNING file_id"
                ),
                {"cid": conv_uuid, "fid": uuid.UUID(fid), "bid": uuid.UUID(bucket_id)},
            )
            if res.fetchone() is not None:
                saved.append(fid)
    await db.execute(
        text("UPDATE conversations SET file_scope_active = :a WHERE id = :cid"),
        {"a": active, "cid": conv_uuid},
    )
    await db.commit()
    return {"file_ids": saved, "scoped": active}


@router.get("/{bucket_id}/conversations", response_model=ConversationListResponse)
async def list_conversations(
    bucket_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    conversations = await list_conversations_service(
        db,
        tctx["owner_id"],
        bucket_id,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )
    return {
        "conversations": [ConversationResponse.model_validate(item) for item in conversations],
        "total": len(conversations),
    }


@router.post("/{bucket_id}/conversations", response_model=ConversationResponse)
async def create_conversation(
    bucket_id: str,
    body: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    conversation = await create_conversation_service(
        db,
        tctx["owner_id"],
        bucket_id,
        title=body.title,
        web_search_mode=body.web_search_mode,
        follow_up_mode=body.follow_up_mode,
        created_by_team_member_id=tctx["team_member_id"],
    )
    return ConversationResponse.model_validate(conversation)


@router.delete("/{bucket_id}/conversations/{conversation_id}", response_model=DeleteConversationResponse)
async def delete_conversation(
    bucket_id: str,
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    await delete_conversation_service(
        db,
        tctx["owner_id"],
        bucket_id,
        conversation_id,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )
    return {"message": "Conversation deleted.", "conversation_id": conversation_id}


@router.get("/{bucket_id}/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    bucket_id: str,
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    messages = await list_conversation_messages(
        db,
        tctx["owner_id"],
        bucket_id,
        conversation_id,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )
    await _attach_senders(db, messages, ctx, uuid.UUID(bucket_id), tctx)
    return {
        "messages": messages,
        "total": len(messages),
    }


@router.post("/{bucket_id}/conversations/{conversation_id}/messages", response_model=AgentReplyResponse)
async def send_message(
    bucket_id: str,
    conversation_id: str,
    body: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    await enforce_chat_quota(db, uuid.UUID(tctx["owner_id"]))
    try:
        result = await run_conversation_turn(
            db,
            user_id=tctx["owner_id"],
            bucket_id=bucket_id,
            conversation_id=conversation_id,
            content=body.content,
            web_search_override=body.web_search,
            agentic_mode=body.agentic_mode,
            acting_team_member_id=tctx["team_member_id"],
            can_read_others_threads=tctx["can_read_others_threads"],
        )
    except Exception as exc:
        await db.rollback()
        await create_notification(
            db,
            str(ctx.user_id),
            "error",
            "AI reply failed",
            f'The assistant could not reply in this conversation. {str(exc)[:220]}',
            commit=True,
        )
        raise
    await _attach_senders(
        db,
        [result.user_message, result.assistant_message],
        ctx,
        uuid.UUID(bucket_id),
        tctx,
    )
    return {
        "conversation": result.conversation,
        "user_message": result.user_message,
        "assistant_message": result.assistant_message,
        "sources": result.sources,
        "used_web_search": result.used_web_search,
        "follow_up_required": result.follow_up_required,
        "action_required": result.action_required,
        "action_type": result.action_type,
        "action_options": result.action_options,
        "thinking_steps": result.thinking_steps,
        "thinking_step_events": result.thinking_step_events,
        "plan": result.plan,
    }


@router.post("/{bucket_id}/conversations/{conversation_id}/messages/stream")
async def send_message_stream(
    bucket_id: str,
    conversation_id: str,
    body: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    """Streams agent step events as Server-Sent Events, then a final `done` event with the full reply payload."""
    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    await enforce_chat_quota(db, uuid.UUID(tctx["owner_id"]))
    queue: asyncio.Queue = asyncio.Queue()
    DONE = object()

    async def on_step(event: dict) -> None:
        kind = event.get("type")
        if kind == "plan_update":
            await queue.put({"kind": "plan_update", "plan": event.get("plan") or []})
        elif kind == "token":
            await queue.put({"kind": "token", "text": event.get("text") or ""})
        else:
            await queue.put({"kind": "step", "event": event})

    async def run_agent():
        try:
            result = await run_conversation_turn(
                db,
                user_id=tctx["owner_id"],
                bucket_id=bucket_id,
                conversation_id=conversation_id,
                content=body.content,
                web_search_override=body.web_search,
                agentic_mode=body.agentic_mode,
                on_step=on_step,
                acting_team_member_id=tctx["team_member_id"],
                can_read_others_threads=tctx["can_read_others_threads"],
            )
            await _attach_senders(
                db,
                [result.user_message, result.assistant_message],
                ctx,
                uuid.UUID(bucket_id),
                tctx,
            )
            payload = {
                "conversation": ConversationResponse.model_validate(result.conversation).model_dump(mode="json"),
                "user_message": _serialize_message(result.user_message),
                "assistant_message": _serialize_message(result.assistant_message),
                "sources": result.sources,
                "used_web_search": result.used_web_search,
                "follow_up_required": result.follow_up_required,
                "action_required": result.action_required,
                "action_type": result.action_type,
                "action_options": result.action_options,
                "thinking_steps": result.thinking_steps,
                "thinking_step_events": result.thinking_step_events,
                "plan": result.plan,
            }
            await queue.put({"kind": "done", "result": payload})
        except Exception as exc:
            await db.rollback()
            await create_notification(
                db,
                str(ctx.user_id),
                "error",
                "AI reply failed",
                f'The assistant could not reply in this conversation. {str(exc)[:220]}',
                commit=True,
            )
            await queue.put({"kind": "error", "message": str(exc)[:500]})
        finally:
            await queue.put(DONE)

    async def event_stream():
        agent_task = asyncio.create_task(run_agent())
        try:
            while True:
                item = await queue.get()
                if item is DONE:
                    break
                yield f"data: {json.dumps(item)}\n\n"
        finally:
            if not agent_task.done():
                agent_task.cancel()
            try:
                await agent_task
            except (asyncio.CancelledError, Exception):
                pass

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


def _serialize_message(message) -> dict:
    """Match MessageResponse shape used by the non-streaming endpoint."""
    from app.schemas.agent import MessageResponse
    return MessageResponse.model_validate(message).model_dump(mode="json")


async def _build_owner_sender(db: AsyncSession, owner_id: uuid.UUID) -> MessageSender:
    prof_q = await db.execute(select(Profile).where(Profile.user_id == owner_id))
    profile = prof_q.scalar_one_or_none()
    name = profile.full_name if profile and profile.full_name else None
    if not name:
        user_q = await db.execute(select(User).where(User.id == owner_id))
        u = user_q.scalar_one_or_none()
        name = u.email if u else "Owner"
    return MessageSender(kind="owner", display_name=name, display_color="#6366F1")


async def _attach_senders(
    db: AsyncSession,
    messages: list,
    ctx: UserContext,
    bucket_uuid: uuid.UUID,
    tctx: dict,
) -> None:
    """Mutate each Message-like object to expose .sender for response serialization.

    Visibility: owner sees everyone. Member sees own bubble normally; for others'
    bubbles, only show name+color when can_see_other_members is true for the
    bucket — otherwise render as 'Team Member' with neutral gray.
    """
    owner_sender = await _build_owner_sender(db, uuid.UUID(tctx["owner_id"]))

    show_other_members = True
    if ctx.is_member:
        access = await get_bucket_access(db, ctx.team_member_id, bucket_uuid)
        show_other_members = bool(access and access.can_see_other_members)

    member_ids = {
        m.sender_team_member_id for m in messages
        if m.sender_team_member_id is not None
    }
    member_rows: dict[uuid.UUID, TeamMember] = {}
    if member_ids:
        rows = await db.execute(
            select(TeamMember).where(TeamMember.id.in_(member_ids))
        )
        member_rows = {tm.id: tm for tm in rows.scalars().all()}

    for msg in messages:
        if msg.role == "assistant":
            msg.sender = MessageSender(kind="assistant")
            continue
        if msg.sender_team_member_id is None:
            msg.sender = owner_sender
            continue

        tm = member_rows.get(msg.sender_team_member_id)
        if tm is None:
            msg.sender = MessageSender(kind="team_member_hidden", display_name="Team Member", display_color="#9CA3AF")
            continue

        is_self = ctx.is_member and ctx.team_member_id == tm.id
        if is_self or show_other_members or not ctx.is_member:
            msg.sender = MessageSender(
                kind="team_member",
                display_name=tm.display_name,
                display_color=tm.display_color,
                team_member_id=tm.id,
            )
        else:
            msg.sender = MessageSender(
                kind="team_member_hidden",
                display_name="Team Member",
                display_color="#9CA3AF",
            )


@router.delete("/{bucket_id}/conversations/{conversation_id}/messages/from/{message_id}")
async def delete_messages_from_endpoint(
    bucket_id: str,
    conversation_id: str,
    message_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    await delete_messages_from_service(
        db,
        tctx["owner_id"],
        bucket_id,
        conversation_id,
        message_id,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )
    return {"message": "Messages deleted.", "from_message_id": message_id}


@router.post("/{bucket_id}/conversations/{conversation_id}/auto-title", response_model=ConversationResponse)
async def auto_title_conversation(
    bucket_id: str,
    conversation_id: str,
    body: AutoTitleRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    title = await generate_short_title(body.message)
    conversation = await rename_conversation_service(
        db,
        tctx["owner_id"],
        bucket_id,
        conversation_id,
        title,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )
    return ConversationResponse.model_validate(conversation)


@router.patch("/{bucket_id}/conversations/{conversation_id}", response_model=ConversationResponse)
async def rename_conversation(
    bucket_id: str,
    conversation_id: str,
    body: RenameConversationRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    conversation = await rename_conversation_service(
        db,
        tctx["owner_id"],
        bucket_id,
        conversation_id,
        body.title,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )
    return ConversationResponse.model_validate(conversation)


@router.patch("/{bucket_id}/conversations/{conversation_id}/pin", response_model=ConversationResponse)
async def pin_conversation(
    bucket_id: str,
    conversation_id: str,
    body: PinConversationRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    conversation = await pin_conversation_service(
        db,
        tctx["owner_id"],
        bucket_id,
        conversation_id,
        body.is_pinned,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )
    return ConversationResponse.model_validate(conversation)


@router.post(
    "/{bucket_id}/conversations/{conversation_id}/messages/{message_id}/feedback",
    response_model=MessageFeedbackResponse,
)
async def submit_message_feedback(
    bucket_id: str,
    conversation_id: str,
    message_id: str,
    body: MessageFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    from app.services.agent.service import get_conversation_for_user

    tctx = await _resolve_thread_ctx(db, ctx, bucket_id)
    await get_conversation_for_user(
        db,
        tctx["owner_id"],
        bucket_id,
        conversation_id,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )

    feedback = MessageFeedback(
        message_id=uuid.UUID(message_id),
        user_id=ctx.user_id,
        rating=body.rating,
        reason=body.reason,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return MessageFeedbackResponse(
        message_id=feedback.message_id,
        rating=feedback.rating,
        reason=feedback.reason,
    )


class SaveMessageAsFileRequest(BaseModel):
    file_name: str
    content: str


@router.post("/{bucket_id}/conversations/{conversation_id}/messages/{message_id}/save-as-file")
async def save_message_as_file(
    bucket_id: str,
    conversation_id: str,
    message_id: str,
    body: SaveMessageAsFileRequest,
    db: AsyncSession = Depends(get_db),
    ctx: UserContext = Depends(get_user_context),
):
    from app.services.agent.tools import write_file as tool_write_file
    from app.services.agent.service import get_conversation_for_user

    tctx = await _resolve_thread_ctx(db, ctx, bucket_id, require="can_upload_files")
    await get_conversation_for_user(
        db,
        tctx["owner_id"],
        bucket_id,
        conversation_id,
        acting_team_member_id=tctx["team_member_id"],
        can_read_others_threads=tctx["can_read_others_threads"],
    )
    result = await tool_write_file(
        db,
        bucket_id=uuid.UUID(bucket_id),
        user_id=uuid.UUID(tctx["owner_id"]),
        file_name=body.file_name,
        content=body.content,
    )
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error or "Failed to save file.")
    return {"file_id": str(result.file_id), "file_name": result.file_name, "r2_path": result.r2_path}
