"""
Step 03 — render document pages to PNG screenshots.
Ported from Aiveilix-pipline; only the FileType import path changed.
"""

import io
import logging
from dataclasses import dataclass

import fitz
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

from app.services.processing_v3.normalize import FileType

logger = logging.getLogger(__name__)

PDF_RENDER_SCALE = 2.0  # native bboxes must be multiplied by this to match screenshot coords

PAGE_W = 1240
PAGE_H = 1754
MARGIN = 40
LINE_HEIGHT = 22
FONT_SIZE = 15
MAX_LINES = 78
CHARS_PER_LINE = 105

MAX_PAGES = 500
MAX_PIXELS_PER_PAGE = 50_000_000
Image.MAX_IMAGE_PIXELS = MAX_PIXELS_PER_PAGE


@dataclass
class RenderedPage:
    page_number: int
    width: int
    height: int
    data: bytes


def render_pages(file_type: FileType, data: bytes) -> list[RenderedPage]:
    if file_type == FileType.PDF:
        return _render_pdf(data)
    if file_type == FileType.IMAGE:
        return _render_image(data)
    if file_type == FileType.TEXT:
        return _render_text(data)
    if file_type == FileType.DOCX:
        raise NotImplementedError("DOCX rendering not installed yet")
    if file_type == FileType.PPTX:
        raise NotImplementedError("PPTX rendering not installed yet")
    raise ValueError(f"Cannot render file type: {file_type}")


def _render_pdf(data: bytes) -> list[RenderedPage]:
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:
        raise ValueError(f"Invalid PDF: {exc}") from exc

    try:
        if doc.needs_pass:
            raise ValueError("Password-protected PDF — cannot render without decryption key")

        page_count = doc.page_count
        if page_count == 0:
            raise ValueError("PDF has no pages")
        if page_count > MAX_PAGES:
            raise ValueError(f"PDF too large: {page_count} pages exceeds limit of {MAX_PAGES}")

        pages = []
        for i, page in enumerate(doc, start=1):
            rect = page.rect
            base_w = rect.width * PDF_RENDER_SCALE
            base_h = rect.height * PDF_RENDER_SCALE
            scale = PDF_RENDER_SCALE
            if base_w * base_h > MAX_PIXELS_PER_PAGE:
                area = max(rect.width * rect.height, 1.0)
                scale = (MAX_PIXELS_PER_PAGE / area) ** 0.5
                logger.warning("render_pdf_page_downscaled page=%s reduced_scale=%.3f", i, scale)
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat)
            pages.append(RenderedPage(
                page_number=i,
                width=pix.width,
                height=pix.height,
                data=pix.tobytes("png"),
            ))
        return pages
    finally:
        doc.close()


def _render_image(data: bytes) -> list[RenderedPage]:
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        img = img.convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("Invalid image: cannot identify format") from exc
    except Image.DecompressionBombError as exc:
        raise ValueError(f"Image too large: exceeds {Image.MAX_IMAGE_PIXELS} pixel limit") from exc
    except Exception as exc:
        raise ValueError(f"Invalid image: {exc}") from exc

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return [RenderedPage(page_number=1, width=img.width, height=img.height, data=buf.getvalue())]


def _render_text(data: bytes) -> list[RenderedPage]:
    text = data.decode("utf-8", errors="replace")
    raw_lines: list[str] = []
    for line in text.splitlines():
        while len(line) > CHARS_PER_LINE:
            raw_lines.append(line[:CHARS_PER_LINE])
            line = line[CHARS_PER_LINE:]
        raw_lines.append(line)

    chunks = [raw_lines[i:i + MAX_LINES] for i in range(0, max(len(raw_lines), 1), MAX_LINES)]
    if len(chunks) > MAX_PAGES:
        raise ValueError(f"Text too large: {len(chunks)} pages exceeds limit of {MAX_PAGES}")

    pages: list[RenderedPage] = []
    font = ImageFont.load_default(size=FONT_SIZE)

    for page_num, chunk in enumerate(chunks, start=1):
        img = Image.new("RGB", (PAGE_W, PAGE_H), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        y = MARGIN
        for line in chunk:
            draw.text((MARGIN, y), line, fill=(20, 20, 20), font=font)
            y += LINE_HEIGHT
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        pages.append(RenderedPage(page_number=page_num, width=PAGE_W, height=PAGE_H, data=buf.getvalue()))

    return pages
