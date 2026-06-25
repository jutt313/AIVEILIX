"""Convert container/office formats we don't natively parse into Markdown,
so they can ride the existing ``FileType.TEXT`` pipeline.

Today's pipeline natively handles PDF / PPTX / DOCX / images / text. XLSX,
EPub and ZIP previously failed at file-type detection. Instead of teaching
each downstream stage about these formats, we convert them to Markdown bytes
at the extraction boundary and let them flow through the text rails (single
synthetic page, no OCR / no visual extraction, just chunking + embedding).

One dependency does the work: Microsoft's ``markitdown``. Pure Python, runs
locally, no API calls — so the converter is effectively free at runtime.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


CONVERTIBLE_EXTS = {"xlsx", "xls", "epub", "zip"}


def convert_to_markdown(file_bytes: bytes, filename: str) -> bytes | None:
    """Return UTF-8 markdown bytes for xlsx/xls/epub/zip, else ``None``.

    Never raises — on any failure we log and return ``None`` so the
    orchestrator can fall through to normal detection (which will mark the
    file failed cleanly with the existing ``Unsupported file type`` path).

    ZIP behaviour: MarkItDown's zip converter walks the archive and
    concatenates each member's markdown, so the whole zip becomes ONE
    searchable document (and counts as 1 against the owner's quota).
    """
    if not filename or "." not in filename:
        return None
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in CONVERTIBLE_EXTS:
        return None
    if not file_bytes:
        return None
    try:
        # Lazy-import so the rest of the pipeline doesn't pay markitdown's
        # import cost on every file. markitdown 0.1.x signature.
        import io
        from markitdown import MarkItDown

        md = MarkItDown(enable_plugins=False)
        # markitdown infers the converter from the stream's extension hint.
        result = md.convert_stream(io.BytesIO(file_bytes), file_extension="." + ext)
        text = (getattr(result, "text_content", None) or "").strip()
        if not text:
            logger.info("markitdown convert returned empty text file=%s ext=%s", filename, ext)
            return None
        return text.encode("utf-8", errors="replace")
    except Exception as exc:
        logger.warning("markitdown convert failed file=%s ext=%s: %s", filename, ext, exc)
        return None
