"""
Provider adapter — translates the harness's neutral tool schema into each
provider's native shape, and normalizes responses into one type.

One interface used by the runner:

    client = build_llm_client(provider)
    reply = await client.chat(system_prompt, messages, tools)

`reply` is always one of:
    Reply(kind="text", text=..., narration_lines=[...])
    Reply(kind="tool_calls", calls=[ToolCall(...)], narration_lines=[...])
    Reply(kind="error", error=...)
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import uuid as _uuid
from dataclasses import dataclass, field
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────── data shapes ──

@dataclass(slots=True)
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]


@dataclass(slots=True)
class Reply:
    kind: str   # "text" | "tool_calls" | "error"
    text: str | None = None
    calls: list[ToolCall] = field(default_factory=list)
    narration_lines: list[str] = field(default_factory=list)
    error: str | None = None


# ─────────────────────────────────────────────────────── provider resolution ──

PROVIDER_ALIASES = {
    "gpt4o": "openai",
    "gpt-4o": "openai",
    "moonshot": "kimi",
    "anthropic": "claude",
    "google": "gemini",
}

# Providers that use OpenAI-compatible function calling.
OPENAI_STYLE = {"openai", "deepseek", "kimi", "minimax"}


def _looks_configured(secret: str) -> bool:
    value = (secret or "").strip()
    return bool(value) and not value.startswith("your-")


def configured_providers() -> list[str]:
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
    if _looks_configured(getattr(settings, "minimax_api_key", "")):
        providers.append("minimax")
    return providers


def resolve_provider(preferred: str | None) -> str:
    """Pick a provider — env preference, then any configured fallback."""
    selected = (preferred or settings.llm_provider or "auto").strip().lower()
    selected = PROVIDER_ALIASES.get(selected, selected)
    configured = configured_providers()
    default = PROVIDER_ALIASES.get((settings.llm_provider or "auto").strip().lower(),
                                   (settings.llm_provider or "auto").strip().lower())

    if selected == "auto":
        if default not in ("", "auto") and default in configured:
            return default
        return configured[0] if configured else "claude"

    if selected in configured:
        return selected

    if default not in ("", "auto") and default in configured:
        logger.warning("[LLM] preferred provider %s unavailable, using %s", selected, default)
        return default
    if configured:
        logger.warning("[LLM] preferred provider %s unavailable, using %s", selected, configured[0])
        return configured[0]
    return selected


# ───────────────────────────────────────────────────────── base + dispatcher ──

class LLMClient:
    """Provider-agnostic chat interface. Implementations override `chat`."""

    native_tools: bool = True
    provider: str = "?"

    async def chat(
        self,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> Reply:
        raise NotImplementedError


def build_llm_client(preferred: str | None = None) -> LLMClient:
    provider = resolve_provider(preferred)
    if provider == "claude":
        return _ClaudeClient(provider)
    if provider == "gemini":
        return _GeminiClient(provider)
    if provider in OPENAI_STYLE:
        return _OpenAIStyleClient(provider)
    # Unknown configured providers fall back to a ReAct text loop.
    return _ReActClient(provider)


# ──────────────────────────────────────────────────────────────────── Claude ──

class _ClaudeClient(LLMClient):
    """Anthropic native tool_use protocol."""

    native_tools = True

    def __init__(self, provider: str):
        self.provider = provider
        self._model = "claude-3-5-sonnet-latest"

    def _translate_tools(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["params_schema"],
            }
            for t in tools
        ]

    def _translate_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for m in messages:
            role = m.get("role")
            if role == "system":
                continue
            if role == "user":
                content = m.get("content")
                if isinstance(content, list):
                    out.append({"role": "user", "content": content})
                else:
                    out.append({"role": "user", "content": str(content or "")})
                continue
            if role == "assistant":
                blocks: list[dict[str, Any]] = []
                text = m.get("content")
                if text:
                    blocks.append({"type": "text", "text": str(text)})
                for c in m.get("tool_calls", []) or []:
                    blocks.append({
                        "type": "tool_use",
                        "id": c["id"],
                        "name": c["name"],
                        "input": c["args"],
                    })
                if blocks:
                    out.append({"role": "assistant", "content": blocks})
                continue
            if role == "tool":
                out.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": m["tool_call_id"],
                        "content": str(m["content"]),
                    }],
                })
        return out

    async def chat(self, system_prompt, messages, tools):
        try:
            from anthropic import AsyncAnthropic
        except Exception as exc:
            return Reply(kind="error", error=f"anthropic SDK missing: {exc}")
        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        try:
            response = await client.messages.create(
                model=self._model,
                max_tokens=4096,
                system=system_prompt,
                messages=self._translate_messages(messages),
                tools=self._translate_tools(tools) if tools else [],
            )
        except Exception as exc:
            logger.exception("[CLAUDE] chat failed: %s", exc)
            return Reply(kind="error", error=str(exc))

        text_parts: list[str] = []
        calls: list[ToolCall] = []
        for block in response.content:
            btype = getattr(block, "type", "")
            if btype == "text":
                text_parts.append(getattr(block, "text", ""))
            elif btype == "tool_use":
                calls.append(ToolCall(
                    id=str(block.id),
                    name=str(block.name),
                    args=dict(block.input or {}),
                ))

        narration = [t.strip() for t in text_parts if t and t.strip()]
        if calls:
            return Reply(kind="tool_calls", calls=calls, narration_lines=narration)
        return Reply(kind="text", text="\n\n".join(narration).strip(), narration_lines=[])


# ──────────────────────────────────────────────────────── OpenAI-style chats ──

class _OpenAIStyleClient(LLMClient):
    """Works for OpenAI, DeepSeek, Kimi, MiniMax — all share the same chat completions API."""

    native_tools = True

    def __init__(self, provider: str):
        self.provider = provider
        if provider == "openai":
            self._model = "gpt-4o"
            self._api_key = settings.openai_api_key
            self._base_url = None
        elif provider == "deepseek":
            self._model = "deepseek-chat"
            self._api_key = settings.deepseek_api_key
            self._base_url = settings.deepseek_base_url
        elif provider == "kimi":
            self._model = "moonshot-v1-8k"
            self._api_key = settings.moonshot_api_key
            self._base_url = settings.moonshot_base_url
        elif provider == "minimax":
            self._model = getattr(settings, "minimax_model", "abab6.5s-chat")
            self._api_key = getattr(settings, "minimax_api_key", "")
            self._base_url = getattr(settings, "minimax_base_url", "https://api.minimaxi.chat/v1")
        else:
            self._model = "gpt-4o"
            self._api_key = settings.openai_api_key
            self._base_url = None

    def _translate_tools(self, tools):
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["params_schema"],
                },
            }
            for t in tools
        ]

    def _translate_messages(self, system_prompt, messages):
        out: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        for m in messages:
            role = m.get("role")
            if role == "system":
                continue
            if role in ("user", "assistant"):
                content = m.get("content")
                payload: dict[str, Any] = {"role": role, "content": str(content or "")}
                tool_calls = m.get("tool_calls") or []
                if role == "assistant" and tool_calls:
                    payload["tool_calls"] = [
                        {
                            "id": c["id"],
                            "type": "function",
                            "function": {
                                "name": c["name"],
                                "arguments": json.dumps(c["args"]),
                            },
                        } for c in tool_calls
                    ]
                out.append(payload)
            elif role == "tool":
                out.append({
                    "role": "tool",
                    "tool_call_id": m["tool_call_id"],
                    "content": str(m["content"]),
                })
        return out

    async def chat(self, system_prompt, messages, tools):
        try:
            from openai import AsyncOpenAI
        except Exception as exc:
            return Reply(kind="error", error=f"openai SDK missing: {exc}")
        if not _looks_configured(self._api_key):
            return Reply(kind="error", error=f"{self.provider} not configured")
        client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)
        try:
            response = await client.chat.completions.create(
                model=self._model,
                temperature=0.2,
                messages=self._translate_messages(system_prompt, messages),
                tools=self._translate_tools(tools) if tools else None,
            )
        except Exception as exc:
            logger.exception("[%s] chat failed: %s", self.provider, exc)
            return Reply(kind="error", error=str(exc))

        if not response.choices:
            return Reply(kind="error", error="empty response")

        choice = response.choices[0].message
        text = (choice.content or "").strip()
        tool_calls = getattr(choice, "tool_calls", None) or []
        calls: list[ToolCall] = []
        for tc in tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
            calls.append(ToolCall(
                id=str(tc.id or _uuid.uuid4()),
                name=str(tc.function.name),
                args=args,
            ))
        narration = [text] if text else []
        if calls:
            return Reply(kind="tool_calls", calls=calls, narration_lines=narration)
        return Reply(kind="text", text=text)


# ──────────────────────────────────────────────────────────── Google Gemini ──

class _GeminiClient(LLMClient):
    """Gemini function-declarations protocol."""

    native_tools = True

    def __init__(self, provider: str):
        self.provider = provider
        self._model = "gemini-2.5-flash"

    def _translate_tools(self, tools):
        return [{
            "function_declarations": [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["params_schema"],
                } for t in tools
            ]
        }]

    def _to_gemini_history(self, messages):
        out = []
        for m in messages:
            role = m.get("role")
            if role == "system":
                continue
            if role == "user":
                content = m.get("content")
                out.append({"role": "user", "parts": [{"text": str(content or "")}]})
            elif role == "assistant":
                parts = []
                if m.get("content"):
                    parts.append({"text": str(m["content"])})
                for c in m.get("tool_calls", []) or []:
                    parts.append({"function_call": {"name": c["name"], "args": c["args"]}})
                if parts:
                    out.append({"role": "model", "parts": parts})
            elif role == "tool":
                out.append({
                    "role": "user",
                    "parts": [{
                        "function_response": {
                            "name": m.get("tool_name") or "tool",
                            "response": {"result": str(m["content"])},
                        }
                    }],
                })
        return out

    async def chat(self, system_prompt, messages, tools):
        try:
            import google.generativeai as genai
        except Exception as exc:
            return Reply(kind="error", error=f"google-generativeai SDK missing: {exc}")
        if not _looks_configured(settings.gemini_api_key):
            return Reply(kind="error", error="gemini not configured")

        def _sync_call():
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(
                model_name=self._model,
                system_instruction=system_prompt,
                tools=self._translate_tools(tools) if tools else None,
            )
            # Send the FULL turn — including the most recent tool result — in a
            # single generate_content call. The old start_chat/send_message split
            # used messages[:-1] for history and dropped messages[-1] when it was
            # a tool result (it sent the literal "(continue)" instead). That meant
            # Gemini never saw what the just-run tool returned and answered blind,
            # hallucinating from the file name. Translating every message keeps each
            # function_response paired with its function_call.
            contents = self._to_gemini_history(messages)
            if not contents:
                contents = [{"role": "user", "parts": [{"text": ""}]}]
            return model.generate_content(contents)

        try:
            response = await asyncio.to_thread(_sync_call)
        except Exception as exc:
            logger.exception("[GEMINI] chat failed: %s", exc)
            return Reply(kind="error", error=str(exc))

        text_parts: list[str] = []
        calls: list[ToolCall] = []
        try:
            candidate = response.candidates[0]
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    text_parts.append(part.text)
                if hasattr(part, "function_call") and part.function_call and part.function_call.name:
                    fc = part.function_call
                    raw_args = dict(fc.args) if fc.args else {}
                    calls.append(ToolCall(
                        id=str(_uuid.uuid4()),
                        name=fc.name,
                        args=raw_args,
                    ))
        except Exception as exc:
            logger.warning("[GEMINI] could not parse response: %s", exc)

        narration = [t.strip() for t in text_parts if t.strip()]
        if calls:
            return Reply(kind="tool_calls", calls=calls, narration_lines=narration)
        return Reply(kind="text", text="\n\n".join(narration).strip())


# ──────────────────────────────────────────── ReAct text-mode fallback client ──

_ACTION_RE = re.compile(r"^\s*ACTION:\s*([a-z_]+)\s*(\{.*\})?\s*$", re.IGNORECASE | re.MULTILINE)
_ANSWER_RE = re.compile(r"^\s*ANSWER:\s*(.+)$", re.IGNORECASE | re.MULTILINE | re.DOTALL)


class _ReActClient(LLMClient):
    """Text-protocol fallback. The model emits ACTION:/ANSWER: lines.

    Used when native tool calling is unreliable (or unconfigured). Same brain,
    same tools, text protocol. We use Anthropic as the underlying chat engine
    because it's the most consistent at following structured text formats —
    but any chat-completion provider could back this.
    """

    native_tools = False

    def __init__(self, provider: str):
        self.provider = provider
        # Fall back to ANY configured chat provider for the underlying call.
        configured = configured_providers()
        self._underlying = configured[0] if configured else "claude"

    def _tools_doc(self, tools):
        lines = ["Available tools:"]
        for t in tools:
            lines.append(f"- {t['name']}: {t['description']}")
            params = t.get("params_schema") or {}
            for k, v in (params.get("properties") or {}).items():
                desc = v.get("description") if isinstance(v, dict) else ""
                lines.append(f"    {k}: {desc}")
        lines.append("")
        lines.append(
            "Format every message exactly as:\n"
            "THOUGHT: <one short line about what you'll do or learned>\n"
            "ACTION: <tool_name> {\"arg\": \"value\", ...}\n"
            "OR when finished:\n"
            "THOUGHT: <one short line>\n"
            "ANSWER: <your final reply to the user>"
        )
        return "\n".join(lines)

    async def chat(self, system_prompt, messages, tools):
        text_prompt = system_prompt + "\n\n" + self._tools_doc(tools)
        underlying = build_llm_client(self._underlying)
        # Reuse the underlying chat without tools — pure text protocol.
        reply = await underlying.chat(text_prompt, messages, tools=[])
        if reply.kind != "text":
            return reply

        text = (reply.text or "").strip()
        answer_match = _ANSWER_RE.search(text)
        if answer_match:
            return Reply(kind="text", text=answer_match.group(1).strip())

        action_match = _ACTION_RE.search(text)
        if action_match:
            name = action_match.group(1).strip()
            raw_args = action_match.group(2) or "{}"
            try:
                args = json.loads(raw_args)
            except Exception:
                args = {}
            return Reply(
                kind="tool_calls",
                calls=[ToolCall(id=str(_uuid.uuid4()), name=name, args=args)],
                narration_lines=[
                    line for line in text.splitlines()
                    if line.strip().upper().startswith("THOUGHT:")
                ],
            )

        # Nothing parseable → treat as final text.
        return Reply(kind="text", text=text)
