"""
Section-outline cleaning — shared by ingest (processing_v3) and the MCP serving
layer so both produce the same clean, structured outline.

Layout parsers over-tag headings on dense pages (marketing/landing pages
especially): they promote split heading lines, paragraph fragments and repeated
CTAs to `type == "heading"`. Raw outlines therefore contain a lot of prose
noise. `clean_section_outline` filters that noise, de-duplicates, normalizes the
text and attaches a 1-based `index` + a heuristic `level` so callers get a
structured, render-ready outline.

The function is pure and idempotent: cleaning an already-clean outline yields the
same result, so it is safe to apply at both ingest and serve time.
"""

from __future__ import annotations

import re

_WS_RE = re.compile(r"\s+")
_LEADING_NUM_RE = re.compile(r"^\s*\d+\s*[.)]\s+")
# A sentence break ("…. ", "…, ") followed by a lowercase word ⇒ prose, not a heading.
_INTERNAL_BREAK_RE = re.compile(r"[.,;:]\s+[a-z]")
# Trailing connective / dangling hyphen ⇒ a heading line cut mid-phrase.
_DANGLING_END_RE = re.compile(r"(?:\b(?:and|or|the|with|to|for|of|a|an|in|on|as|is|are)\b|-)$", re.I)

MAX_HEADING_WORDS = 12
MAX_HEADING_CHARS = 80


def normalize_heading(text: str | None) -> str:
    """Collapse whitespace / non-breaking spaces / newlines to single spaces."""
    return _WS_RE.sub(" ", (text or "").replace(" ", " ")).strip()


def _looks_like_prose(heading: str) -> bool:
    """True when the heading is really a paragraph/sentence fragment, not a heading."""
    body = _LEADING_NUM_RE.sub("", heading)  # ignore "1. " / "2) " numbering
    if not body:
        return True
    if len(body) > MAX_HEADING_CHARS or len(body.split()) > MAX_HEADING_WORDS:
        return True
    if _INTERNAL_BREAK_RE.search(body):
        return True
    if _DANGLING_END_RE.search(body):
        return True
    first_alpha = next((c for c in body if c.isalpha()), "")
    if first_alpha and first_alpha.islower():  # continuation fragment
        return True
    return False


def _heading_level(heading: str) -> int:
    """Cheap 2-level heuristic: short / all-caps ⇒ top level, else sub-level."""
    body = _LEADING_NUM_RE.sub("", heading)
    if body.isupper() or len(body.split()) <= 4:
        return 1
    return 2


def clean_section_outline(raw: list[dict] | None) -> list[dict]:
    """
    Turn a raw [{heading, page}, …] list into a clean, structured outline:
    [{index, level, page, heading}, …] with prose fragments removed, repeats
    de-duplicated and headings normalized. Order is preserved.
    """
    cleaned: list[dict] = []
    seen: set[str] = set()
    for entry in raw or []:
        heading = normalize_heading(entry.get("heading", ""))
        if not heading or _looks_like_prose(heading):
            continue
        key = heading.lower()
        if key in seen:  # drop repeated CTAs / duplicate headings
            continue
        seen.add(key)
        cleaned.append({
            "index": len(cleaned) + 1,
            "level": _heading_level(heading),
            "page": entry.get("page"),
            "heading": heading,
        })
    return cleaned


def outline_to_markdown(outline: list[dict] | None) -> str:
    """Render a cleaned outline as an indented markdown list with page refs."""
    lines = []
    for e in outline or []:
        indent = "  " * (int(e.get("level", 1)) - 1)
        page = e.get("page")
        suffix = f" _(p{page})_" if page is not None else ""
        lines.append(f"{indent}- {e.get('heading', '')}{suffix}")
    return "\n".join(lines)
