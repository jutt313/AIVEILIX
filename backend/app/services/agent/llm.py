from __future__ import annotations

import asyncio
import logging
import re
from typing import Iterable

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional runtime dependency
    genai = None

try:
    from anthropic import AsyncAnthropic
except Exception:  # pragma: no cover - optional runtime dependency
    AsyncAnthropic = None

try:
    from openai import AsyncOpenAI
except Exception:  # pragma: no cover - optional runtime dependency
    AsyncOpenAI = None

from app.config import settings
from app.services.agent.prompts import ANSWER_SYSTEM_PROMPT
from app.services.agent.retrieval import RetrievedDocumentChunk, RetrievedMemoryChunk, RetrievedWebResult


def _looks_configured(secret: str) -> bool:
    value = (secret or "").strip()
    if not value:
        return False
    return not value.startswith("your-")


def _configured_providers() -> list[str]:
    providers: list[str] = []
    if _looks_configured(settings.anthropic_api_key):
        providers.append("claude")
    if _looks_configured(settings.gemini_api_key):
        providers.append("gemini")
    if _looks_configured(settings.openai_api_key):
        providers.append("openai")
    if _looks_configured(settings.deepseek_api_key):
        providers.append("deepseek")
    if _looks_configured(settings.moonshot_api_key):
        providers.append("kimi")
    return providers


def select_provider(preferred_llm: str | None) -> str:
    selected = (preferred_llm or settings.llm_provider or "auto").strip().lower()
    alias_map = {
        "gpt4o": "openai",
        "gpt-4o": "openai",
        "moonshot": "kimi",
    }
    selected = alias_map.get(selected, selected)
    configured = _configured_providers()
    default_provider = alias_map.get((settings.llm_provider or "auto").strip().lower(), (settings.llm_provider or "auto").strip().lower())

    if selected == "auto":
        if default_provider not in ("", "auto") and default_provider in configured:
            return default_provider
        return configured[0] if configured else "claude"

    if selected in configured:
        return selected

    if default_provider not in ("", "auto") and default_provider in configured:
        logger.warning("[LLM] preferred provider %s unavailable, falling back to %s", selected, default_provider)
        return default_provider

    if configured:
        logger.warning("[LLM] preferred provider %s unavailable, falling back to %s", selected, configured[0])
        return configured[0]

    return selected


def infer_style_guidance(message: str, recent_user_messages: Iterable[str]) -> str:
    recent = list(recent_user_messages)
    average_length = sum(len(item) for item in recent + [message]) / max(len(recent) + 1, 1)
    if "short" in message.lower() or average_length < 80:
        return "Keep the answer concise in wording, but never drop or skip a fact you found — completeness over brevity for factual lookups."
    if any(token in message.lower() for token in ("detail", "detailed", "deep", "step by step", "explain")):
        return "Provide a detailed, technical answer with enough context to understand the reasoning."
    return "Match the user's tone and keep the answer focused and practical."


def build_answer_prompt(
    *,
    question: str,
    style_guidance: str,
    document_chunks: list[RetrievedDocumentChunk],
    memory_chunks: list[RetrievedMemoryChunk],
    web_results: list[RetrievedWebResult],
) -> tuple[str, str]:
    document_context = "\n\n".join(
        (
            f"[Document {idx}] {chunk.file_name} overview\n{chunk.content}"
            if chunk.is_summary
            else f"[Document {idx}] {chunk.file_name} page {chunk.page}\n{chunk.content}"
        )
        for idx, chunk in enumerate(document_chunks, start=1)
    ) or "No relevant bucket documents found."

    memory_context = "\n\n".join(
        f"[Memory {idx}] ({chunk.role}) {chunk.content}"
        for idx, chunk in enumerate(memory_chunks, start=1)
    ) or "No relevant thread memory found."

    web_context = "\n\n".join(
        f"[Web {idx}] {result.title}\nURL: {result.url}\n{result.snippet}"
        for idx, result in enumerate(web_results, start=1)
    ) or "No web results used."

    has_documents = bool(document_chunks)
    has_web = bool(web_results)

    system_prompt = ANSWER_SYSTEM_PROMPT
    if has_web:
        system_prompt += (
            "\n\nIMPORTANT: Live web search results have already been fetched for you and are "
            "included in this prompt under 'Web results'. You DO have access to current web data "
            "for this turn. Use those results to answer. NEVER tell the user you can't browse "
            "the web, can't search online, or don't have a browsing tool — that is false in this "
            "turn. Cite the web result titles/URLs naturally in your answer when you draw from them."
        )

    transparency_note = (
        " Be transparent if you are drawing from general knowledge rather than the bucket."
        if not has_documents and not has_web else ""
    )
    user_prompt = (
        f"User question:\n{question}\n\n"
        f"Style guidance:\n{style_guidance}\n\n"
        "Priority rule:\n"
        "- Bucket documents are the primary evidence when they are relevant to the user's question.\n"
        "- Use conversation memory / recent chat to resolve follow-ups, pronouns, and user-provided context.\n"
        "- If the bucket documents do not contain the answer but recent chat does, answer from recent chat and cite memory.\n"
        "- If documents and chat conflict, say which answer comes from documents and which comes from chat.\n\n"
        f"Conversation memory (context from this thread):\n{memory_context}\n\n"
        f"Bucket documents:\n{document_context}\n\n"
        f"Web results (LIVE — already fetched for you, use these directly):\n{web_context}\n\n"
        "OUTPUT FORMAT (strict, two parts):\n"
        "1. The answer body. Do NOT include a 'Sources:' list — that is appended automatically.\n"
        "2. On the VERY LAST line, output the citation marker exactly:\n"
        "   USED: D1,D3,W2\n"
        "   List ONLY [Document #] and [Web #] items whose content you actually drew from. "
        "If you used none of them, write: USED: none\n"
        "The USED line is mandatory on every response and is stripped before the user sees it. "
        "Do not skip it, do not wrap it in quotes, do not put anything after it."
        + transparency_note
    )
    return system_prompt, user_prompt


async def _generate_with_claude(system_prompt: str, user_prompt: str, chat_history: list[dict[str, str]] | None = None) -> str | None:
    if AsyncAnthropic is None or not _looks_configured(settings.anthropic_api_key):
        return None
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    msgs: list[dict[str, str]] = []
    if chat_history:
        msgs.extend(chat_history)
    msgs.append({"role": "user", "content": user_prompt})
    response = await client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=900,
        system=system_prompt,
        messages=msgs,
    )
    return "".join(part.text for part in response.content if getattr(part, "type", "") == "text").strip() or None


async def _generate_with_openai(system_prompt: str, user_prompt: str, *, model: str, api_key: str, base_url: str | None = None, chat_history: list[dict[str, str]] | None = None) -> str | None:
    if AsyncOpenAI is None or not _looks_configured(api_key):
        return None
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    msgs: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if chat_history:
        msgs.extend(chat_history)
    msgs.append({"role": "user", "content": user_prompt})
    response = await client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=msgs,
    )
    return response.choices[0].message.content.strip() if response.choices else None


def _generate_with_gemini_sync(system_prompt: str, user_prompt: str, chat_history: list[dict[str, str]] | None = None) -> str | None:
    if genai is None or not _looks_configured(settings.gemini_api_key):
        return None
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_prompt)
    if chat_history:
        gem_history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in chat_history
        ]
        chat = model.start_chat(history=gem_history)
        response = chat.send_message(user_prompt)
    else:
        response = model.generate_content(user_prompt)
    return (response.text or "").strip() or None


async def _generate_with_gemini(system_prompt: str, user_prompt: str, chat_history: list[dict[str, str]] | None = None) -> str | None:
    return await asyncio.to_thread(_generate_with_gemini_sync, system_prompt, user_prompt, chat_history)


def _clean_fallback_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


_THREAD_CONTEXT_FALLBACK_TRIGGERS = (
    "my name", "what is my", "whst is my", "what was my", "whst was my",
    "what did i", "whst did i", "what i said", "what did you say",
    "what have i", "what have we", "what were we", "what are we",
    "last message", "previous message", "prior message", "earlier", "before",
    "above", "just now", "this chat", "this thread", "this conversation",
    "our conversation", "remember", "remind me", "i told you", "you told me",
    "we discussed", "we talked", "talking about",
)


def _looks_like_thread_context_question(question: str) -> bool:
    lowered = f" {question.lower()} "
    return any(trigger in lowered for trigger in _THREAD_CONTEXT_FALLBACK_TRIGGERS)


# Matches the trailing "USED: D1,D3" citation marker whether it sits on its own
# line OR inline at the end of a sentence ("…Rolling Stone. USED: D1,D3"). The
# `\b` guards against false hits inside words like "focused:" / "unused:".
_USED_LINE_RE = re.compile(
    r"(?im)[\s>*\-•]*\**\s*\bUSED\b\**\s*:\**\s*([^\n]*?)\s*\**\s*$"
)


def extract_used_marker(answer: str) -> tuple[str, set[int] | None, set[int] | None]:
    """
    Parse the trailing 'USED: D1,D3,W2' line the LLM was asked to emit.

    Returns (cleaned_answer, doc_indices, web_indices). Indices are 1-based and
    refer to [Document N] / [Web N] in the prompt. `None` means the marker was
    absent — caller should fall back to including everything that was retrieved.
    `set()` (empty) means the model explicitly said "USED: none".
    """
    matches = list(_USED_LINE_RE.finditer(answer))
    if not matches:
        logger.warning("[CITE] USED marker missing — falling back to all retrieved sources")
        return answer.rstrip(), None, None

    last = matches[-1]
    cleaned = (answer[: last.start()] + answer[last.end():]).rstrip()
    raw = last.group(1).strip().strip("*").strip()

    if not raw or raw.lower() in {"none", "n/a", "[]", "-"}:
        return cleaned, set(), set()

    doc_idx: set[int] = set()
    web_idx: set[int] = set()
    for token in re.split(r"[,\s;]+", raw):
        token = token.strip().strip("[]()").upper()
        if not token:
            continue
        m = re.match(r"^(D|W|DOC|WEB|DOCUMENT)\s*#?\s*(\d+)$", token)
        if not m:
            continue
        kind = m.group(1)
        num = int(m.group(2))
        if num < 1:
            continue
        if kind in ("D", "DOC", "DOCUMENT"):
            doc_idx.add(num)
        elif kind in ("W", "WEB"):
            web_idx.add(num)
    logger.info("[CITE] USED parsed: docs=%s web=%s (raw=%r)", sorted(doc_idx), sorted(web_idx), raw)
    return cleaned, doc_idx, web_idx


def build_fallback_answer(
    question: str,
    document_chunks: list[RetrievedDocumentChunk],
    memory_chunks: list[RetrievedMemoryChunk],
    web_results: list[RetrievedWebResult],
    chat_history: list[dict[str, str]] | None = None,
) -> str:
    prefer_thread_context = _looks_like_thread_context_question(question)

    if prefer_thread_context and memory_chunks:
        lead = memory_chunks[0].content.strip()
        return _clean_fallback_text(f"Based on our conversation so far: {lead}")

    if prefer_thread_context and chat_history:
        recent = " ".join(
            f"{item.get('role', 'user').title()}: {item.get('content', '').strip()}"
            for item in chat_history[-4:]
            if item.get("content")
        )
        if recent:
            return _clean_fallback_text(f"Based on our conversation so far: {recent}")

    if document_chunks:
        lead = document_chunks[0].content.strip()
        body = f"Here's what I found in your documents: {lead}"
        if web_results:
            body += f" Also from the web: {web_results[0].snippet.strip() or web_results[0].title.strip()}."
        return _clean_fallback_text(body)

    if web_results:
        lead = web_results[0].snippet.strip() or web_results[0].title.strip()
        return _clean_fallback_text(f"I didn't find that in your documents, but here's what the web says: {lead}")

    if memory_chunks:
        lead = memory_chunks[0].content.strip()
        return _clean_fallback_text(f"Based on our conversation so far: {lead}")

    if chat_history:
        recent = " ".join(
            f"{item.get('role', 'user').title()}: {item.get('content', '').strip()}"
            for item in chat_history[-4:]
            if item.get("content")
        )
        if recent:
            return _clean_fallback_text(f"Based on our conversation so far: {recent}")

    return (
        "Hmm, I don't have enough info in this bucket to answer that. "
        "Try uploading some documents or give me more context!"
    )


async def generate_answer(
    *,
    question: str,
    preferred_llm: str | None,
    style_guidance: str,
    document_chunks: list[RetrievedDocumentChunk],
    memory_chunks: list[RetrievedMemoryChunk],
    web_results: list[RetrievedWebResult],
    chat_history: list[dict[str, str]] | None = None,
) -> str:
    system_prompt, user_prompt = build_answer_prompt(
        question=question,
        style_guidance=style_guidance,
        document_chunks=document_chunks,
        memory_chunks=memory_chunks,
        web_results=web_results,
    )

    provider = select_provider(preferred_llm)
    logger.info("[LLM] provider=%s history=%d", provider, len(chat_history or []))
    try:
        if provider == "claude":
            answer = await _generate_with_claude(system_prompt, user_prompt, chat_history=chat_history)
        elif provider == "gemini":
            answer = await _generate_with_gemini(system_prompt, user_prompt, chat_history=chat_history)
        elif provider == "openai":
            answer = await _generate_with_openai(system_prompt, user_prompt, model="gpt-4o", api_key=settings.openai_api_key, chat_history=chat_history)
        elif provider == "deepseek":
            answer = await _generate_with_openai(
                system_prompt,
                user_prompt,
                model="deepseek-chat",
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                chat_history=chat_history,
            )
        elif provider == "kimi":
            answer = await _generate_with_openai(
                system_prompt,
                user_prompt,
                model="moonshot-v1-8k",
                api_key=settings.moonshot_api_key,
                base_url=settings.moonshot_base_url,
                chat_history=chat_history,
            )
        else:
            answer = None
        if answer:
            logger.info("[LLM] %s → %d chars", provider, len(answer))
            return answer
    except Exception as exc:
        logger.exception("[LLM] %s call failed: %s", provider, exc)

    logger.warning("[LLM] fallback triggered — no answer from %s", provider)
    return build_fallback_answer(question, document_chunks, memory_chunks, web_results, chat_history=chat_history)


async def generate_raw_completion(
    *,
    system_prompt: str,
    user_prompt: str,
    preferred_llm: str | None,
    chat_history: list[dict[str, str]] | None = None,
) -> str | None:
    """Low-level LLM call that returns raw text without any RAG prompt wrapping.

    Reuses provider selection and per-provider functions so planning calls
    benefit from the same fallback logic as answer generation.
    Returns None only when every configured provider fails.
    """
    provider = select_provider(preferred_llm)
    logger.info("[LLM:raw] provider=%s", provider)
    try:
        if provider == "claude":
            return await _generate_with_claude(system_prompt, user_prompt, chat_history=chat_history)
        elif provider == "gemini":
            return await _generate_with_gemini(system_prompt, user_prompt, chat_history=chat_history)
        elif provider == "openai":
            return await _generate_with_openai(
                system_prompt, user_prompt,
                model="gpt-4o", api_key=settings.openai_api_key,
                chat_history=chat_history,
            )
        elif provider == "deepseek":
            return await _generate_with_openai(
                system_prompt, user_prompt,
                model="deepseek-chat",
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                chat_history=chat_history,
            )
        elif provider == "kimi":
            return await _generate_with_openai(
                system_prompt, user_prompt,
                model="moonshot-v1-8k",
                api_key=settings.moonshot_api_key,
                base_url=settings.moonshot_base_url,
                chat_history=chat_history,
            )
    except Exception as exc:
        logger.exception("[LLM:raw] %s call failed: %s", provider, exc)
    return None


async def rewrite_query_with_history(
    *,
    question: str,
    chat_history: list[dict[str, str]],
    preferred_llm: str | None = None,
) -> str:
    """Create a standalone retrieval query from the current message plus recent chat."""
    clean_question = (question or "").strip()
    if not clean_question or not chat_history:
        return clean_question

    compact_history = "\n".join(
        f"{item.get('role', 'user')}: {item.get('content', '').strip()[:500]}"
        for item in chat_history[-3:]
        if item.get("content")
    )
    if not compact_history:
        return clean_question

    system_prompt = (
        "Rewrite the user's current message into one standalone search query for retrieving bucket documents. "
        "Use recent chat only to resolve references, pronouns, and user-provided facts. "
        "Do not answer the question. Do not add facts not present in the recent chat. "
        "Return one concise query only."
    )
    user_prompt = (
        f"Recent chat:\n{compact_history}\n\n"
        f"Current message:\n{clean_question}\n\n"
        "Standalone retrieval query:"
    )
    try:
        rewritten = await asyncio.wait_for(
            generate_raw_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                preferred_llm=preferred_llm,
            ),
            timeout=4.0,
        )
    except Exception:
        rewritten = None

    rewritten = (rewritten or "").strip().strip('"').strip("'")
    if not rewritten:
        return f"{compact_history}\nCurrent question: {clean_question}"
    return rewritten[:1000]


TITLE_SYSTEM_PROMPT = (
    "You generate ultra-short chat titles. Reply with ONLY the title, no quotes, no punctuation, "
    "no explanation. Maximum 2 words. Total length must be at most 10 characters including the space. "
    "Use Title Case. Examples: 'Auth Bug', 'API Help', 'CSV Parse', 'DB Slow'."
)


def _fallback_short_title(text: str) -> str:
    clean = re.sub(r"@\S+", "", text or "").strip()
    clean = re.sub(r"[^A-Za-z0-9\s]", " ", clean)
    words = [w for w in clean.split() if w]
    if not words:
        return "Chat"
    picked: list[str] = []
    total = 0
    for w in words[:2]:
        extra = (1 if picked else 0) + len(w)
        if total + extra > 10:
            break
        picked.append(w)
        total += extra
    if not picked:
        picked = [words[0][:10]]
    return " ".join(p.capitalize() for p in picked)


def _sanitize_title(raw: str | None, fallback_source: str) -> str:
    if not raw:
        return _fallback_short_title(fallback_source)
    title = raw.strip().strip('"').strip("'").splitlines()[0].strip()
    title = re.sub(r"[\.!?,:;]+$", "", title)
    title = re.sub(r"\s+", " ", title)
    if not title:
        return _fallback_short_title(fallback_source)
    if len(title) > 10:
        words = title.split()
        truncated: list[str] = []
        total = 0
        for w in words[:2]:
            extra = (1 if truncated else 0) + len(w)
            if total + extra > 10:
                break
            truncated.append(w)
            total += extra
        title = " ".join(truncated) if truncated else title[:10].rstrip()
    return " ".join(p[:1].upper() + p[1:] for p in title.split() if p) or _fallback_short_title(fallback_source)


async def generate_short_title(message: str) -> str:
    source = (message or "").strip()
    if not source:
        return "Chat"
    user_prompt = f"First user message:\n{source[:600]}\n\nTitle:"
    provider = select_provider(None)
    raw: str | None = None
    try:
        if provider == "gemini":
            raw = await _generate_with_gemini(TITLE_SYSTEM_PROMPT, user_prompt)
        elif provider == "claude":
            raw = await _generate_with_claude(TITLE_SYSTEM_PROMPT, user_prompt)
        elif provider == "openai":
            raw = await _generate_with_openai(TITLE_SYSTEM_PROMPT, user_prompt, model="gpt-4o-mini", api_key=settings.openai_api_key)
        elif provider == "deepseek":
            raw = await _generate_with_openai(TITLE_SYSTEM_PROMPT, user_prompt, model="deepseek-chat", api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
        elif provider == "kimi":
            raw = await _generate_with_openai(TITLE_SYSTEM_PROMPT, user_prompt, model="moonshot-v1-8k", api_key=settings.moonshot_api_key, base_url=settings.moonshot_base_url)
    except Exception as exc:
        logger.warning("[LLM] title generation failed (%s): %s", provider, exc)
    return _sanitize_title(raw, source)
