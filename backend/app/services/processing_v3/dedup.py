"""
Step 07b — content-level dedup of layout elements (pipeline v3).

The visual-understanding stage frequently emits the same magazine quote, review
screenshot, or product photo more than once (overlapping crops of one region,
or the same testimonial repeated down a landing page). The geometric IOU dedup
in ``visual_elements.py`` only catches overlapping *bounding boxes* on a single
page; this pass catches semantically identical *content* across the whole doc.

It runs in the orchestrator on the merged element list BEFORE summary, export,
and chunking, so the stored layout JSON (what ``list_visuals`` serves), the
summary, and the chunks are all built from the de-duplicated set — i.e. it fixes
the *stored* data, not just retrieval context.

Recall-safe:
  * only true near-identicals collapse (high default threshold);
  * dedup is scoped *within a modality* — a visual asset is never folded into a
    body-text element, and vice versa;
  * the surviving representative keeps ``dup_count`` + ``duplicate_ids`` so
    nothing is silently lost (and "quoted 3x" stays recoverable).
"""

from __future__ import annotations

import logging

from app.services.processing_v3.layout import ElementRecord
from app.services.processing_v3.text_sim import bucket_key, normalize_text, similarity

logger = logging.getLogger(__name__)


def _compare_text(elem: ElementRecord) -> str:
    """Text used to judge duplication: content + any visible (in-image) text."""
    meta = elem.metadata or {}
    parts = [elem.content or ""]
    vis = meta.get("visible_text")
    if vis:
        parts.append(str(vis))
    return " ".join(p for p in parts if p).strip()


def _modality(elem: ElementRecord) -> str:
    """Duplicates only collapse within the same modality."""
    return "visual" if elem.source == "visual_understanding" else "text"


def _quality(elem: ElementRecord) -> tuple[float, int, int]:
    """Higher is better when choosing which duplicate to keep as representative."""
    conf = elem.confidence if isinstance(elem.confidence, (int, float)) else 0.0
    return (float(conf), len(_compare_text(elem)), -elem.sort_order)


def _snapshot(elem: ElementRecord) -> dict:
    """Full audit record of a dropped duplicate. Preserves where it sat and what
    it was (page, bbox, source/type, text, asset) so a collapse is never a black
    box — surfaced via the layout JSON, list_visuals, and get_visual."""
    meta = elem.metadata or {}
    return {
        "id": elem.id,
        "page_number": elem.page_number,
        "sort_order": elem.sort_order,
        "type": elem.type,
        "source": elem.source,
        "content": elem.content or "",
        "visible_text": meta.get("visible_text"),
        "asset_uri": meta.get("asset_uri"),
        "bbox": elem.bbox,
        "confidence": elem.confidence,
    }


def dedupe_elements(
    elements: list[ElementRecord],
    *,
    threshold: float = 0.90,
) -> tuple[list[ElementRecord], list[dict]]:
    """Collapse near-identical elements. Returns (kept_elements, report).

    Greedy single-pass clustering with a normalized-prefix blocking key keeps
    this ~O(n) in practice rather than O(n^2). Empty-text elements are always
    kept untouched.
    """
    if not elements:
        return elements, []

    clusters: list[list[int]] = []           # each cluster = list of element indices
    exact_map: dict[tuple[str, str], int] = {}   # (modality, norm) -> cluster idx
    bucket_map: dict[tuple[str, str], list[int]] = {}  # (modality, prefix) -> cluster idxs

    for i, elem in enumerate(elements):
        text = _compare_text(elem)
        norm = normalize_text(text)
        if not norm:
            clusters.append([i])  # nothing to match on — standalone
            continue

        mod = _modality(elem)
        ci = exact_map.get((mod, norm))

        if ci is None:
            bkey = (mod, bucket_key(text))
            for cand in bucket_map.get(bkey, []):
                rep_idx = clusters[cand][0]
                if similarity(text, _compare_text(elements[rep_idx])) >= threshold:
                    ci = cand
                    break

        if ci is None:
            ci = len(clusters)
            clusters.append([i])
            exact_map[(mod, norm)] = ci
            bucket_map.setdefault((mod, bucket_key(text)), []).append(ci)
        else:
            clusters[ci].append(i)
            exact_map.setdefault((mod, norm), ci)

    kept: list[ElementRecord] = []
    report: list[dict] = []
    for members in clusters:
        if len(members) == 1:
            kept.append(elements[members[0]])
            continue
        rep_idx = max(members, key=lambda m: _quality(elements[m]))
        rep = elements[rep_idx]
        dropped = [elements[m] for m in members if m != rep_idx]
        rep.metadata = {
            **(rep.metadata or {}),
            "dup_count": len(members),
            "duplicate_ids": [d.id for d in dropped],
            "duplicate_snapshots": [_snapshot(d) for d in dropped],
        }
        kept.append(rep)
        report.append({
            "kept_id": rep.id,
            "type": rep.type,
            "page": rep.page_number,
            "dropped": len(dropped),
            "sample": _compare_text(rep)[:80],
        })

    removed = len(elements) - len(kept)
    if removed:
        logger.info(
            "dedup_elements in=%s out=%s removed=%s clusters_collapsed=%s",
            len(elements), len(kept), removed, len(report),
        )
    return kept, report
