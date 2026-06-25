"""
Auto-category classification for pipeline v3.

One cheap Gemini-flash-lite call per file reuses the already-computed summary
text as context. Falls back to a filename/file-type label on any error so
processing never blocks on classification.

Used by orchestrator's finalize path (lite tier today; can be enabled for the
full tier too) to populate ``files.category_id`` so the bucket UI can show a
category chip on every file row.
"""

from __future__ import annotations

import asyncio
import logging
import re

from app.config import settings

logger = logging.getLogger(__name__)

# Hard cap on how many words make it into the stored category name. Anything
# above this is trimmed (a model that ignores "1-2 words" still gets bounded).
_MAX_WORDS = 3
_MAX_CHARS = 40

_PROMPT = (
    "Classify this document into ONE short category (1-2 words). "
    "Reply with ONLY the category name — no quotes, no punctuation, no extra text.\n\n"
    "Examples of good categories: Finance, Legal, Research, Marketing, Product, "
    "HR, Sales, Engineering, Support, Strategy.\n\n"
    "Document: {filename}\n\nSummary:\n{summary}"
)


def _fallback_from_filename(filename: str) -> str:
    """Last-resort label when no LLM is available or the call errors out."""
    name = (filename or "").strip().lower()
    if name.endswith(".pdf"):
        return "PDF"
    if name.endswith((".ppt", ".pptx")):
        return "Slides"
    if name.endswith((".doc", ".docx")):
        return "Document"
    if name.endswith((".xls", ".xlsx", ".csv")):
        return "Spreadsheet"
    if name.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
        return "Image"
    if name.endswith((".md", ".txt")):
        return "Notes"
    return "Uncategorized"


def _clean(raw: str, filename: str) -> str:
    """Strip punctuation and clamp to 1-2 words / _MAX_CHARS."""
    text = (raw or "").strip()
    # Strip Markdown emphasis, code fences, and surrounding quotes.
    text = re.sub(r"^[`*_'\"\s]+|[`*_'\"\s.,!?:]+$", "", text)
    # Take only the first line.
    text = text.splitlines()[0] if text else ""
    if not text:
        return _fallback_from_filename(filename)
    # Collapse internal whitespace.
    words = text.split()
    words = words[:_MAX_WORDS]
    cleaned = " ".join(words)[:_MAX_CHARS].strip()
    return cleaned or _fallback_from_filename(filename)


async def classify_document(filename: str, summary_text: str) -> str:
    """Return a 1-2 word category for a document. Never raises."""
    if not summary_text or not settings.gemini_api_key:
        return _fallback_from_filename(filename)

    prompt = _PROMPT.format(
        filename=filename or "(unnamed)",
        summary=(summary_text or "")[:6000],
    )

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_visual_model)

        def _call():
            return model.generate_content(prompt)

        response = await asyncio.get_event_loop().run_in_executor(None, _call)
        raw = (response.text or "").strip()
        return _clean(raw, filename)
    except Exception as exc:
        logger.warning("auto-category failed for %s: %s", filename, exc)
        return _fallback_from_filename(filename)
