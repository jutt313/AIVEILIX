"""
Step 06 — layout element building (native text + OCR → ElementRecord).
Ported from Aiveilix-pipline; import paths changed.
"""

import logging
import statistics
import uuid
from dataclasses import dataclass

from app.services.processing_v3.ocr import OCRResult
from app.services.processing_v3.render import PDF_RENDER_SCALE
from app.services.processing_v3.native_text import NativeTextBlock

logger = logging.getLogger(__name__)

HEADING_LINE_HEIGHT_RATIO = 1.5
HEADING_MAX_LINES = 3
HEADING_MIN_LINE_HEIGHT_PT = 16


@dataclass
class ElementRecord:
    id: str
    doc_id: str
    page_id: str
    page_number: int
    type: str
    content: str
    bbox: list[float] | None
    source: str
    confidence: float | None
    metadata: dict
    sort_order: int


def _to_xywh(bbox: tuple[float, float, float, float], scale: float = 1.0) -> list[float]:
    x0, y0, x1, y1 = bbox
    return [x0 * scale, y0 * scale, (x1 - x0) * scale, (y1 - y0) * scale]


def _page_line_heights(blocks: list[NativeTextBlock]) -> list[float]:
    heights = []
    for b in blocks:
        if b.bbox:
            h = b.bbox[3] - b.bbox[1]
            num_lines = max(1, b.text.count("\n") + 1)
            heights.append(h / num_lines)
    return heights


def _classify_native_type(
    text: str,
    bbox: tuple[float, float, float, float] | None,
    page_line_heights: list[float],
) -> str:
    if not bbox:
        return "paragraph"
    h = bbox[3] - bbox[1]
    num_lines = max(1, text.count("\n") + 1)
    line_height = h / num_lines
    if num_lines > HEADING_MAX_LINES:
        return "paragraph"
    if line_height >= HEADING_MIN_LINE_HEIGHT_PT:
        return "heading"
    if page_line_heights:
        median_lh = statistics.median(page_line_heights)
        if median_lh > 0 and line_height >= HEADING_LINE_HEIGHT_RATIO * median_lh:
            return "heading"
    return "paragraph"


def build_elements(
    doc_id: str,
    native_blocks: list[NativeTextBlock],
    ocr_results: dict[int, OCRResult],
    page_ocr_status: dict[int, str],
    page_ids: dict[int, str],
) -> list[ElementRecord]:
    native_by_page: dict[int, list[NativeTextBlock]] = {}
    for block in native_blocks:
        native_by_page.setdefault(block.page_number, []).append(block)

    elements: list[ElementRecord] = []

    for page_num in sorted(page_ocr_status):
        page_id = page_ids[page_num]
        status = page_ocr_status[page_num]

        if status == "skipped":
            page_blocks = native_by_page.get(page_num, [])
            page_lh = _page_line_heights(page_blocks)
            for i, block in enumerate(page_blocks):
                element_type = _classify_native_type(block.text, block.bbox, page_lh)
                elements.append(ElementRecord(
                    id=str(uuid.uuid4()),
                    doc_id=doc_id,
                    page_id=page_id,
                    page_number=page_num,
                    type=element_type,
                    content=block.text,
                    bbox=_to_xywh(block.bbox, scale=PDF_RENDER_SCALE) if block.bbox else None,
                    source="native_text",
                    confidence=None,
                    metadata={},
                    sort_order=i,
                ))
        else:
            ocr = ocr_results.get(page_num)
            if ocr is None:
                logger.warning("build_elements_missing_ocr_result page=%s status=%s", page_num, status)
                continue
            if ocr.text:
                elements.append(ElementRecord(
                    id=str(uuid.uuid4()),
                    doc_id=doc_id,
                    page_id=page_id,
                    page_number=page_num,
                    type="paragraph",
                    content=ocr.text,
                    bbox=None,
                    source="ocr",
                    confidence=None,
                    metadata={"provider": ocr.provider, "model": ocr.model},
                    sort_order=0,
                ))

    return elements
