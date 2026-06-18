"""
Step 04 — native (selectable) text extraction.
Ported from Aiveilix-pipline; only the FileType import path changed.
"""

import re
from dataclasses import dataclass, field

import fitz

from app.services.processing_v3.normalize import FileType

WEAK_TEXT_THRESHOLD = 20

_CAPTION_NOISE_RE = re.compile(
    r"^\s*(?:png|jpe?g|gif|tiff?|webp|bmp)\s+image\s*\d+\s*[:\-.]",
    re.IGNORECASE,
)


def is_caption_noise(text: str) -> bool:
    return bool(_CAPTION_NOISE_RE.match(text))


@dataclass
class NativeTextBlock:
    page_number: int
    text: str
    bbox: tuple[float, float, float, float] | None
    source: str = field(default="native_text", init=False)


def extract_native_text(file_type: FileType, data: bytes) -> list[NativeTextBlock]:
    if file_type == FileType.PDF:
        return _extract_pdf(data)
    if file_type == FileType.TEXT:
        return _extract_text(data)
    return []


def is_page_text_weak(blocks: list[NativeTextBlock], page_number: int) -> bool:
    total = sum(len(b.text) for b in blocks if b.page_number == page_number)
    return total < WEAK_TEXT_THRESHOLD


def _extract_pdf(data: bytes) -> list[NativeTextBlock]:
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"Invalid PDF: {exc}") from exc

    try:
        blocks: list[NativeTextBlock] = []
        for page_num, page in enumerate(doc, start=1):
            for block in page.get_text("dict").get("blocks", []):
                if block.get("type") != 0:
                    continue
                lines: list[str] = []
                for line in block.get("lines", []):
                    line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                    if line_text.strip():
                        lines.append(line_text)
                text = "\n".join(lines).strip()
                x0, y0, x1, y1 = block["bbox"]
                if x1 < x0:
                    x0, x1 = x1, x0
                if y1 < y0:
                    y0, y1 = y1, y0
                if text and not is_caption_noise(text):
                    blocks.append(NativeTextBlock(page_number=page_num, text=text, bbox=(x0, y0, x1, y1)))
        return blocks
    finally:
        doc.close()


def _extract_text(data: bytes) -> list[NativeTextBlock]:
    text = data.decode("utf-8", errors="replace").strip()
    if not text:
        return []
    return [NativeTextBlock(page_number=1, text=text, bbox=None)]
