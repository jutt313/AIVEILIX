"""
Step 07 — visual element extraction (images, charts, logos, buttons).
Ported from Aiveilix-pipline app/pipeline/step_07_visual_elements.py; import paths changed.

Detection strategy:
- PDFs: PyMuPDF type==1 image blocks + vector-chart detection give exact bboxes.
- Screenshots: colorfulness mask − text bboxes → BFS connected components.
Each region is cropped, uploaded to R2, and described by the visual model.
"""

import asyncio
import collections
import io
import logging
import uuid

import numpy as np
from PIL import Image, ImageFilter

from app.services.processing_v3.storage import R2StorageAdapter
from app.services.processing_v3.visual import VisualUnderstandingProvider
from app.services.processing_v3.render import PDF_RENDER_SCALE
from app.services.processing_v3.layout import ElementRecord

logger = logging.getLogger(__name__)

VISUAL_CONCURRENCY = 30

_COLOR_RANGE_THRESHOLD = 20
_DARK_THRESHOLD = 100
_DARK_COLOR_MIN = 5
_DILATION_SIZE = 21
_BFS_CELL_SIZE = 16
_MIN_REGION_H = 40
_MIN_REGION_W = 60
_MIN_AREA_RATIO = 0.001
_MAX_REGION_H = 1200
_PDF_CONTAINER_AREA_RATIO = 0.60
_PDF_DEDUPE_IOU = 0.88

_ASSET_TYPE_TO_ELEMENT_TYPE: dict[str, str] = {
    "photo": "image",
    "product_photo": "product_image",
    "before_after": "before_after_image",
    "review_screenshot": "review_screenshot",
    "logo": "logo",
    "icon": "icon",
    "button": "cta_button",
    "chart": "chart",
    "text_block": "text",
}


def extract_pdf_image_regions(pdf_data: bytes, page_number: int) -> list[tuple[int, int, int, int]]:
    """Return (x, y, w, h) bboxes for embedded image blocks on a PDF page (1-indexed)."""
    import fitz

    doc = fitz.open(stream=pdf_data, filetype="pdf")
    if page_number < 1 or page_number > len(doc):
        return []
    page = doc[page_number - 1]
    page_w = int(page.rect.width * PDF_RENDER_SCALE)
    page_h = int(page.rect.height * PDF_RENDER_SCALE)
    blocks = page.get_text("dict").get("blocks", [])
    regions: list[tuple[int, int, int, int]] = []
    for block in blocks:
        if block.get("type") != 1:
            continue
        x0, y0, x1, y1 = block["bbox"]
        x = int(x0 * PDF_RENDER_SCALE)
        y = int(y0 * PDF_RENDER_SCALE)
        w = int((x1 - x0) * PDF_RENDER_SCALE)
        h = int((y1 - y0) * PDF_RENDER_SCALE)
        clipped = _clip_region(x, y, w, h, page_w, page_h)
        if clipped is None:
            continue
        x, y, w, h = clipped
        if w >= _MIN_REGION_W and h >= _MIN_REGION_H:
            regions.append((x, y, w, h))
    return _normalize_pdf_image_regions(regions, page_w, page_h)


_CHART_MIN_BARS = 4
_CHART_BAR_MAX_H = 30
_CHART_BAR_MIN_W = 30
_CHART_BAR_MIN_RATIO = 3.0
_CHART_NEAR_BLACK = 0.15
_CHART_NEAR_WHITE = 0.90
_CHART_CARD_MIN_W = 80
_CHART_CARD_MIN_H = 40
_CHART_CARD_MAX_AREA_RATIO = 0.6
_CHART_PAD = 8


def _is_chart_bar(drawing: dict) -> bool:
    if drawing.get("type") not in ("f", "fs"):
        return False
    fill = drawing.get("fill")
    if not fill or max(fill[:3]) < _CHART_NEAR_BLACK:
        return False
    rect = drawing["rect"]
    w, h = rect.width, rect.height
    if h < 4 or h > _CHART_BAR_MAX_H or w < _CHART_BAR_MIN_W:
        return False
    return (w / h) > _CHART_BAR_MIN_RATIO


def _rect_contains(outer, inner, tol: float = 2.0) -> bool:
    return (
        inner.x0 >= outer.x0 - tol and inner.y0 >= outer.y0 - tol
        and inner.x1 <= outer.x1 + tol and inner.y1 <= outer.y1 + tol
    )


def extract_pdf_chart_regions(pdf_data: bytes, page_number: int) -> list[tuple[int, int, int, int]]:
    """Return (x, y, w, h) bboxes for vector charts on a PDF page (1-indexed)."""
    import fitz

    doc = fitz.open(stream=pdf_data, filetype="pdf")
    if page_number < 1 or page_number > len(doc):
        return []
    page = doc[page_number - 1]
    page_w = int(page.rect.width * PDF_RENDER_SCALE)
    page_h = int(page.rect.height * PDF_RENDER_SCALE)
    page_area = page.rect.width * page.rect.height

    drawings = page.get_drawings()
    bars = [d["rect"] for d in drawings if _is_chart_bar(d)]
    if len(bars) < _CHART_MIN_BARS:
        return []

    cards = []
    for d in drawings:
        fill = d.get("fill")
        if d.get("type") in ("f", "fs") and fill and min(fill[:3]) >= _CHART_NEAR_WHITE:
            r = d["rect"]
            if (
                r.width >= _CHART_CARD_MIN_W and r.height >= _CHART_CARD_MIN_H
                and (r.width * r.height) < _CHART_CARD_MAX_AREA_RATIO * page_area
            ):
                cards.append(r)

    raw_regions: list[tuple[float, float, float, float]] = []
    used = [False] * len(bars)

    for card in cards:
        contained = [i for i, b in enumerate(bars) if _rect_contains(card, b)]
        if len(contained) >= _CHART_MIN_BARS:
            raw_regions.append((card.x0, card.y0, card.x1, card.y1))
            for i in contained:
                used[i] = True

    leftover = sorted((b for i, b in enumerate(bars) if not used[i]), key=lambda r: r.y0)
    cluster: list = []
    clusters: list[list] = []
    for bar in leftover:
        if cluster and bar.y0 - cluster[-1].y1 > 4 * _CHART_BAR_MAX_H:
            clusters.append(cluster)
            cluster = []
        cluster.append(bar)
    if cluster:
        clusters.append(cluster)
    for grp in clusters:
        if len(grp) < _CHART_MIN_BARS:
            continue
        raw_regions.append((
            min(b.x0 for b in grp) - _CHART_PAD,
            min(b.y0 for b in grp) - _CHART_PAD,
            max(b.x1 for b in grp) + _CHART_PAD,
            max(b.y1 for b in grp) + _CHART_PAD,
        ))

    regions: list[tuple[int, int, int, int]] = []
    for x0, y0, x1, y1 in raw_regions:
        x = int(x0 * PDF_RENDER_SCALE)
        y = int(y0 * PDF_RENDER_SCALE)
        w = int((x1 - x0) * PDF_RENDER_SCALE)
        h = int((y1 - y0) * PDF_RENDER_SCALE)
        clipped = _clip_region(x, y, w, h, page_w, page_h)
        if clipped is not None:
            regions.append(clipped)
    return regions


def _clip_region(x: int, y: int, w: int, h: int, page_w: int, page_h: int) -> tuple[int, int, int, int] | None:
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(page_w, x + w)
    y1 = min(page_h, y + h)
    if x1 <= x0 or y1 <= y0:
        return None
    return x0, y0, x1 - x0, y1 - y0


def _region_area(region: tuple[int, int, int, int]) -> int:
    return region[2] * region[3]


def _region_iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix0 = max(ax, bx)
    iy0 = max(ay, by)
    ix1 = min(ax + aw, bx + bw)
    iy1 = min(ay + ah, by + bh)
    iw = max(0, ix1 - ix0)
    ih = max(0, iy1 - iy0)
    inter = iw * ih
    if inter == 0:
        return 0.0
    union = _region_area(a) + _region_area(b) - inter
    return inter / union if union else 0.0


def _normalize_pdf_image_regions(
    regions: list[tuple[int, int, int, int]],
    page_w: int,
    page_h: int,
) -> list[tuple[int, int, int, int]]:
    if not regions:
        return []

    page_area = max(1, page_w * page_h)
    container_cutoff = int(page_area * _PDF_CONTAINER_AREA_RATIO)
    has_smaller_regions = any(_region_area(r) < container_cutoff for r in regions)
    filtered = [
        r for r in regions
        if not (has_smaller_regions and _region_area(r) >= container_cutoff)
    ]

    deduped: list[tuple[int, int, int, int]] = []
    for region in sorted(filtered, key=lambda r: (r[1], r[0], -_region_area(r))):
        duplicate_idx = next(
            (idx for idx, existing in enumerate(deduped) if _region_iou(region, existing) >= _PDF_DEDUPE_IOU),
            None,
        )
        if duplicate_idx is None:
            deduped.append(region)
            continue
        if _region_area(region) > _region_area(deduped[duplicate_idx]):
            deduped[duplicate_idx] = region

    return deduped


def detect_visual_regions(
    image_data: bytes,
    text_bboxes: list[list[float]] | None = None,
) -> list[tuple[int, int, int, int]]:
    img = Image.open(io.BytesIO(image_data)).convert("RGB")
    W, H = img.size
    min_area = int(W * H * _MIN_AREA_RATIO)

    arr = np.array(img, dtype=np.float32)
    color_range = arr.max(axis=2) - arr.min(axis=2)
    brightness = arr.mean(axis=2)

    is_visual = (color_range > _COLOR_RANGE_THRESHOLD) | (
        (brightness < _DARK_THRESHOLD) & (color_range > _DARK_COLOR_MIN)
    )

    if text_bboxes:
        for bbox in text_bboxes:
            if not bbox or len(bbox) < 4:
                continue
            bx, by, bw, bh = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            y1 = min(by + bh, H)
            x1 = min(bx + bw, W)
            if y1 > 0 and x1 > 0:
                is_visual[max(0, by):y1, max(0, bx):x1] = False

    visual_img = Image.fromarray((is_visual * 255).astype(np.uint8), "L")
    dilated = visual_img.filter(ImageFilter.MaxFilter(size=_DILATION_SIZE))
    mask = np.array(dilated) > 128

    blobs = _bfs_regions(mask, min_h=_MIN_REGION_H, min_w=_MIN_REGION_W, min_area=min_area)

    result: list[tuple[int, int, int, int]] = []
    for x, y, w, h in blobs:
        result.extend(_split_tall(mask, x, y, w, h))
    return result


def _bfs_regions(mask: np.ndarray, min_h: int, min_w: int, min_area: int) -> list[tuple[int, int, int, int]]:
    H, W = mask.shape
    cs = _BFS_CELL_SIZE

    gh = (H + cs - 1) // cs
    gw = (W + cs - 1) // cs

    grid = np.zeros((gh, gw), dtype=bool)
    for gr in range(gh):
        r0, r1 = gr * cs, min((gr + 1) * cs, H)
        band = mask[r0:r1, :]
        for gc in range(gw):
            c0, c1 = gc * cs, min((gc + 1) * cs, W)
            if band[:, c0:c1].any():
                grid[gr, gc] = True

    visited = np.zeros((gh, gw), dtype=bool)
    rects: list[tuple[int, int, int, int]] = []

    for start_r in range(gh):
        for start_c in range(gw):
            if not grid[start_r, start_c] or visited[start_r, start_c]:
                continue

            q: collections.deque[tuple[int, int]] = collections.deque()
            q.append((start_r, start_c))
            visited[start_r, start_c] = True
            min_gr = max_gr = start_r
            min_gc = max_gc = start_c

            while q:
                r, c = q.popleft()
                if r < min_gr:
                    min_gr = r
                if r > max_gr:
                    max_gr = r
                if c < min_gc:
                    min_gc = c
                if c > max_gc:
                    max_gc = c
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < gh and 0 <= nc < gw and grid[nr, nc] and not visited[nr, nc]:
                        visited[nr, nc] = True
                        q.append((nr, nc))

            px0 = min_gc * cs
            py0 = min_gr * cs
            px1 = min((max_gc + 1) * cs, W)
            py1 = min((max_gr + 1) * cs, H)
            pw = px1 - px0
            ph = py1 - py0
            if pw >= min_w and ph >= min_h and pw * ph >= min_area:
                rects.append((px0, py0, pw, ph))

    return rects


def _split_tall(
    mask: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int,
    max_h: int = _MAX_REGION_H,
) -> list[tuple[int, int, int, int]]:
    """Iteratively split tall regions at low-density rows.

    The original recursive version could infinitely recurse when argmin
    returned 0 (split_row==0 → bot_h==h → same call repeated).
    This iterative version always makes progress and has no recursion risk.
    """
    H, W = mask.shape
    results: list[tuple[int, int, int, int]] = []
    pending: list[tuple[int, int, int, int]] = [(x, y, w, h)]

    while pending:
        cx, cy, cw, ch = pending.pop()

        if ch <= max_h:
            results.append((cx, cy, cw, ch))
            continue

        y2 = min(cy + ch, H)
        x2 = min(cx + cw, W)
        band = mask[cy:y2, cx:x2]
        if band.size == 0:
            continue

        row_density = band.mean(axis=1)
        split_row = int(np.argmin(row_density))
        min_density = float(row_density[split_row])

        if min_density > 0.10:
            logger.debug("visual_region_rejected reason=no_gap x=%s y=%s w=%s h=%s", cx, cy, cw, ch)
            continue

        # Guard: split_row must be strictly inside the region so we always
        # make forward progress. If argmin returns 0 or the last row, we
        # cannot split without producing an identical sub-region → drop.
        if split_row == 0 or split_row >= ch:
            logger.debug("visual_region_rejected reason=split_at_edge x=%s y=%s w=%s h=%s split=%s", cx, cy, cw, ch, split_row)
            continue

        top_h = split_row
        bot_h = ch - split_row
        if top_h >= _MIN_REGION_H:
            pending.append((cx, cy, cw, top_h))
        if bot_h >= _MIN_REGION_H:
            pending.append((cx, cy + split_row, cw, bot_h))

    return results


def crop_region(image_data: bytes, x: int, y: int, w: int, h: int) -> bytes:
    img = Image.open(io.BytesIO(image_data)).convert("RGB")
    cropped = img.crop((x, y, x + w, y + h))
    buf = io.BytesIO()
    cropped.save(buf, format="PNG")
    return buf.getvalue()


async def extract_visual_elements(
    doc_id: str,
    page_id: str,
    page_number: int,
    screenshot_data: bytes,
    storage: R2StorageAdapter,
    visual_provider: VisualUnderstandingProvider,
    sort_order_start: int = 0,
    text_bboxes: list[list[float]] | None = None,
    pdf_image_regions: list[tuple[int, int, int, int]] | None = None,
    semaphore: asyncio.Semaphore | None = None,
) -> list[ElementRecord]:
    if pdf_image_regions:
        regions = pdf_image_regions
        logger.info("visual_regions_from_pdf doc_id=%s page=%s count=%s", doc_id, page_number, len(regions))
    else:
        try:
            regions = detect_visual_regions(screenshot_data, text_bboxes=text_bboxes)
        except Exception as exc:
            logger.warning("visual_detect_failed doc_id=%s page=%s error=%s", doc_id, page_number, exc)
            return []
        logger.info("visual_regions_found doc_id=%s page=%s count=%s", doc_id, page_number, len(regions))

    async def _process_region(i: int, region: tuple[int, int, int, int]) -> ElementRecord | None:
        x, y, w, h = region
        try:
            crop = crop_region(screenshot_data, x, y, w, h)
            asset_name = f"image_{i + 1}.png"
            asset_uri = await storage.upload_page_asset(crop, doc_id, page_number, asset_name)
            understanding = await visual_provider.understand(crop)
        except Exception as exc:
            logger.warning("visual_element_failed doc_id=%s page=%s region=%s error=%s", doc_id, page_number, i, exc)
            return None

        asset_type = str(understanding.get("asset_type") or "unknown")
        summary = str(understanding.get("summary") or "")
        visible_text = str(understanding.get("visible_text") or "")
        had_error = bool(understanding.get("visual_error", False))
        try:
            confidence = float(understanding.get("confidence") or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0

        elem_type = _ASSET_TYPE_TO_ELEMENT_TYPE.get(asset_type, "image")
        content = summary or f"Visual element on page {page_number}"

        meta: dict = {
            "asset_uri": asset_uri,
            "asset_type": asset_type,
            "visible_text": visible_text,
            "confidence": confidence,
        }
        if understanding.get("provider"):
            meta["provider"] = understanding["provider"]
        if understanding.get("model"):
            meta["model"] = understanding["model"]
        if had_error:
            meta["visual_error"] = True

        logger.info(
            "visual_element_extracted doc_id=%s page=%s index=%s type=%s visual_error=%s",
            doc_id, page_number, i, elem_type, had_error,
        )
        return ElementRecord(
            id=str(uuid.uuid4()),
            doc_id=doc_id,
            page_id=page_id,
            page_number=page_number,
            type=elem_type,
            content=content,
            bbox=[float(x), float(y), float(w), float(h)],
            source="visual_understanding",
            confidence=confidence,
            metadata=meta,
            sort_order=sort_order_start + i,
        )

    async def _guarded(i: int, region: tuple[int, int, int, int]) -> ElementRecord | None:
        if semaphore is None:
            return await _process_region(i, region)
        async with semaphore:
            return await _process_region(i, region)

    results = await asyncio.gather(*(_guarded(i, r) for i, r in enumerate(regions)))
    return [e for e in results if e is not None]
