"""
Document summarisation for pipeline v3 — Gemini Flash.

Produces a document-level summary that is stored as a `summaries` row and also
indexed as a pinned summary chunk. Falls back to a heading-based summary if the
Gemini call fails so processing never blocks on it.
"""

import asyncio
import logging

from app.config import settings
from app.services.processing_v3.layout import ElementRecord

logger = logging.getLogger(__name__)

_SUMMARY_PROMPT = """You are summarising a document so that another AI agent can decide \
whether to read it in full. Your summary must be detailed enough that the reader can \
confidently answer high-level questions about the document without opening it, and can \
also tell what KIND of detail is inside.

Respond in this exact format (no extra preamble, no markdown headers other than the \
labels below):

Title: <the document's actual title — infer from headings if no explicit title>
Document Type: <e.g. landing page, contract, research paper, invoice, slide deck, manual, report, article, product page>

Overview:
<4-7 sentences describing what the document is, who produced it, who it is for, what \
it claims or contains, and the overall structure. Be concrete — name brands, products, \
parties, dates, topics. Do NOT write fluff like "Overview of file.pdf".>

Key Points:
- <a specific fact, claim, statistic, section, or feature — at least 6 bullets, more if useful>
- <each bullet should be a complete sentence with real detail, not a heading>
- <cover the full range of the document: intro, body sections, evidence, conclusions, contact/footer>
- <include numbers, names, product names, locations when they appear>

Notable Entities:
<comma-separated list of named entities found: people, brands, organisations, places, \
products, dates>

Keywords:
<comma-separated keywords a user might search to find this document>

Document context:
{context}
"""


def _build_context(filename: str, elements: list[ElementRecord], max_chars: int = 20000) -> str:
    parts = [f"Filename: {filename}"]
    headings, snippets, visuals = [], [], []
    for e in elements:
        content = (e.content or "").strip()
        if not content:
            continue
        if e.type == "heading":
            headings.append(f"[Page {e.page_number}] {content}")
        elif e.source == "visual_understanding":
            if len(visuals) < 25:
                visuals.append(f"[Visual on page {e.page_number}] {content[:300]}")
        elif len(snippets) < 80:
            snippets.append(f"[Page {e.page_number}] {content[:500]}")
    if headings:
        parts += ["Headings:"] + headings[:50]
    if snippets:
        parts += ["Text snippets:"] + snippets
    if visuals:
        parts += ["Visual elements:"] + visuals
    return "\n".join(parts)[:max_chars]


def _fallback_summary(filename: str, elements: list[ElementRecord]) -> str:
    """Heuristic summary used when no LLM is available. Aims to be actually useful:
    real title, opening prose excerpt, multiple heading points, page count, visual count.
    """
    title = ""
    headings: list[str] = []
    prose_snippets: list[str] = []
    visual_count = 0
    pages: set[int] = set()

    for e in elements:
        content = (e.content or "").strip()
        if not content:
            continue
        if e.page_number is not None:
            pages.add(e.page_number)
        if e.source == "visual_understanding":
            visual_count += 1
            continue
        if e.type == "heading":
            # First short heading wins as title — long "headings" are usually paragraphs
            if not title and len(content) <= 120:
                title = content
            normalised = " ".join(content.split())
            if normalised not in headings and len(normalised) <= 200:
                headings.append(normalised)
        else:
            # Collect short, sentence-like text for the overview
            if 30 <= len(content) <= 400 and len(prose_snippets) < 4:
                prose_snippets.append(" ".join(content.split()))

    page_count = len(pages) or 1
    overview_bits = [
        f"This is a {page_count}-page document ({filename}) containing approximately "
        f"{len(headings)} section(s) and {visual_count} visual element(s)."
    ]
    if prose_snippets:
        excerpt = " ".join(prose_snippets[:2])
        if len(excerpt) > 500:
            excerpt = excerpt[:497] + "..."
        overview_bits.append("Opening content: " + excerpt)

    body = [
        f"Title: {title or filename}",
        "Document Type: document",
        "",
        "Overview:",
        " ".join(overview_bits),
    ]
    if headings:
        body += ["", "Key Points:"] + [f"- {h}" for h in headings[:12]]
    body += [
        "",
        "Note: this is a heuristic summary. Call `get_file` for the full document content "
        "or `query` to ask a question across the bucket.",
    ]
    return "\n".join(body).strip()


async def summarise(filename: str, elements: list[ElementRecord]) -> str:
    """Return a summary string. Never raises — falls back on any failure.

    By default this uses the instant heading-based fallback so files become
    searchable in ~15s instead of waiting 60s+ for an LLM summary call. The
    chunks themselves carry all the real content for RAG; the doc-level summary
    is just a pinned overview point. Set settings.processing_v3_ai_summary=True
    to opt back into the slow LLM-generated summary.
    """
    fallback = _fallback_summary(filename, elements)
    if not getattr(settings, "processing_v3_ai_summary", False):
        return fallback

    context = _build_context(filename, elements)
    prompt = _SUMMARY_PROMPT.format(context=context)

    # Prefer Kimi/Moonshot (OpenAI-compatible); fall back to Gemini, then heading-based.
    if settings.moonshot_api_key:
        try:
            import openai

            def _call_kimi():
                client = openai.OpenAI(
                    api_key=settings.moonshot_api_key,
                    base_url=settings.moonshot_base_url,
                    timeout=90,
                )
                resp = client.chat.completions.create(
                    model="kimi-k2.6",
                    messages=[{"role": "user", "content": prompt}],
                )
                return (resp.choices[0].message.content or "").strip()

            text = await asyncio.to_thread(_call_kimi)
            return text or fallback
        except Exception as exc:
            logger.warning("v3 summary (kimi) failed for %s; trying gemini: %s", filename, exc)

    if not settings.gemini_api_key:
        return fallback

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        def _call():
            return model.generate_content(prompt)

        response = await asyncio.get_event_loop().run_in_executor(None, _call)
        text = (response.text or "").strip()
        return text or fallback
    except Exception as exc:
        logger.warning("v3 summary failed for %s; using fallback: %s", filename, exc)
        return fallback
