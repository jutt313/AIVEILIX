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
import re

logger = logging.getLogger(__name__)


CONVERTIBLE_EXTS = {"xlsx", "xls", "epub", "zip"}

# Below this many chars of real body content the conversion is treated as empty
# (an empty archive, a blank sheet) and we fall through to a clean failure.
_MIN_USEFUL_CHARS = 8

# markitdown prefixes a zip's output with a header line like
# "Content from the zip file `name`:" before each member. Strip it so an empty
# archive reads as empty rather than as that placeholder string.
_ZIP_HEADER_RE = re.compile(r"^Content from the zip file .*?:\s*", re.DOTALL)


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

        # Guard 1 — plain-text fallback. xlsx/xls/epub/zip are binary container
        # formats; a real one never decodes cleanly as UTF-8. If markitdown
        # handed back text byte-identical to the decoded input, it fell back to
        # its plain-text converter (e.g. a .txt renamed .xlsx) rather than
        # actually parsing the format. Treat that as unsupported.
        try:
            if text == file_bytes.decode("utf-8").strip():
                logger.info("markitdown plain-text fallback file=%s ext=%s — unsupported", filename, ext)
                return None
        except (UnicodeDecodeError, ValueError):
            pass  # genuine binary file — the expected, healthy path

        # Guard 2 — empty container. Strip markitdown's zip header so an archive
        # with no usable members reads as empty.
        body = _ZIP_HEADER_RE.sub("", text, count=1).strip() if ext == "zip" else text
        if len(body) < _MIN_USEFUL_CHARS:
            logger.info("markitdown convert produced no usable content file=%s ext=%s len=%s",
                        filename, ext, len(body))
            return None

        return text.encode("utf-8", errors="replace")
    except Exception as exc:
        logger.warning("markitdown convert failed file=%s ext=%s: %s", filename, ext, exc)
        return None
