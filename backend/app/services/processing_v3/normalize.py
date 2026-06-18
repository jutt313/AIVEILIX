"""
Step 02 — file-type detection. Ported verbatim from Aiveilix-pipline.
"""

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class FileType(Enum):
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    DOCX = "docx"
    PPTX = "pptx"


_MIME_MAP: dict[str, FileType] = {
    "application/pdf": FileType.PDF,
    "image/jpeg": FileType.IMAGE,
    "image/png": FileType.IMAGE,
    "image/webp": FileType.IMAGE,
    "image/tiff": FileType.IMAGE,
    "image/gif": FileType.IMAGE,
    "text/plain": FileType.TEXT,
    "text/markdown": FileType.TEXT,
    "text/html": FileType.TEXT,
    "text/csv": FileType.TEXT,
    "text/tab-separated-values": FileType.TEXT,
    "text/xml": FileType.TEXT,
    "text/yaml": FileType.TEXT,
    "text/x-yaml": FileType.TEXT,
    "text/x-python": FileType.TEXT,
    "text/x-shellscript": FileType.TEXT,
    "text/x-sql": FileType.TEXT,
    "text/x-log": FileType.TEXT,
    "text/rtf": FileType.TEXT,
    "application/rtf": FileType.TEXT,
    "application/json": FileType.TEXT,
    "application/ld+json": FileType.TEXT,
    "application/xml": FileType.TEXT,
    "application/x-yaml": FileType.TEXT,
    "application/x-toml": FileType.TEXT,
    "application/toml": FileType.TEXT,
    "application/javascript": FileType.TEXT,
    "application/typescript": FileType.TEXT,
    "application/x-httpd-php": FileType.TEXT,
    "application/x-sh": FileType.TEXT,
    "application/sql": FileType.TEXT,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCX,
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": FileType.PPTX,
}

# All extensions that are treated as plain text (some are pre-processed first — see preprocess_text_bytes)
_TEXT_EXTS = {
    "txt", "md", "markdown",
    "json", "jsonl", "ndjson",
    "csv", "tsv",
    "xml", "html", "htm",
    "yaml", "yml",
    "ini", "toml", "env", "cfg", "conf", "properties",
    "log",
    "rtf",
    # code
    "py", "js", "mjs", "cjs", "ts", "tsx", "jsx",
    "java", "kt", "swift", "scala", "groovy",
    "c", "h", "cpp", "cc", "cxx", "hpp", "hh",
    "cs", "go", "rs", "rb", "php", "pl", "lua",
    "sql", "sh", "bash", "zsh", "fish",
    "r", "m", "dart", "vue", "svelte",
}

_EXT_MAP: dict[str, FileType] = {
    "pdf": FileType.PDF,
    "png": FileType.IMAGE,
    "jpg": FileType.IMAGE,
    "jpeg": FileType.IMAGE,
    "webp": FileType.IMAGE,
    "tiff": FileType.IMAGE,
    "tif": FileType.IMAGE,
    "gif": FileType.IMAGE,
    "docx": FileType.DOCX,
    "pptx": FileType.PPTX,
    **{ext: FileType.TEXT for ext in _TEXT_EXTS},
}


def _sniff_magic_bytes(data: bytes) -> FileType | None:
    if data[:5] == b"%PDF-":
        return FileType.PDF
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return FileType.IMAGE
    if data[:3] == b"\xff\xd8\xff":
        return FileType.IMAGE
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return FileType.IMAGE
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return FileType.IMAGE
    if data[:4] in (b"II*\x00", b"MM\x00*"):
        return FileType.IMAGE
    return None


def detect_file_type(mime_type: str, filename: str, data: bytes) -> FileType:
    if not data:
        raise ValueError("Empty file: 0 bytes")

    sniffed = _sniff_magic_bytes(data)
    mime_match = _MIME_MAP.get(mime_type)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    ext_match = _EXT_MAP.get(ext)

    if sniffed is not None:
        if mime_match is not None and mime_match != sniffed:
            logger.warning(
                "file_type_mime_mismatch claimed_mime=%s sniffed=%s filename=%s",
                mime_type, sniffed.value, filename,
            )
        return sniffed

    if mime_match is not None:
        return mime_match
    if ext_match is not None:
        return ext_match
    raise ValueError(f"Unsupported file type: mime={mime_type!r} ext={ext!r}")


def _strip_html(text: str) -> str:
    import re
    from html import unescape
    # Drop <script>/<style> blocks entirely (including content)
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    # Remove all remaining tags
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    # Collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def _strip_rtf(text: str) -> str:
    """Very basic RTF stripper — removes control words and braces. Good enough for indexing."""
    import re
    text = re.sub(r"\\par[d]?", "\n", text)
    text = re.sub(r"\\tab", "\t", text)
    text = re.sub(r"\\'[0-9a-fA-F]{2}", "", text)
    text = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", text)
    text = re.sub(r"[{}]", "", text)
    return text.strip()


def preprocess_text_bytes(data: bytes, filename: str) -> bytes:
    """
    Clean up text-family bytes BEFORE they hit the render/native-text stages.
    HTML/RTF get stripped to plain text; JSON gets pretty-printed for readability.
    Everything else passes through.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in {"html", "htm", "rtf", "json", "jsonl", "ndjson"}:
        return data

    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:
        return data

    if ext in ("html", "htm"):
        cleaned = _strip_html(text)
    elif ext == "rtf":
        cleaned = _strip_rtf(text)
    elif ext == "json":
        try:
            import json
            cleaned = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
        except Exception:
            cleaned = text  # Malformed JSON — index as-is
    elif ext in ("jsonl", "ndjson"):
        try:
            import json
            lines = []
            for raw in text.splitlines():
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    lines.append(json.dumps(json.loads(raw), indent=2, ensure_ascii=False))
                except Exception:
                    lines.append(raw)
            cleaned = "\n\n".join(lines)
        except Exception:
            cleaned = text
    else:
        cleaned = text

    return cleaned.encode("utf-8", errors="replace")
