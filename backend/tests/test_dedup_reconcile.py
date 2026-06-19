"""Unit tests for pipeline-v3 ingestion cleanup: dedup + name reconciliation.

Cases are modeled on the live `norseorganic page.pdf` failures:
  * duplicate Fox News / Glamour quote blocks (list_visuals padding)
  * 'horse organics' (visual misread) vs frequent 'Norse Organics'
  * 'Daniel Hoffman' (signature) vs 'Daniel Hoftun' (body)
"""

import uuid

from app.services.processing_v3.layout import ElementRecord
from app.services.processing_v3.dedup import dedupe_elements
from app.services.processing_v3.reconcile import reconcile_names


def _elem(content, *, source="visual_understanding", etype="text_block",
          visible_text=None, page=1, conf=0.9, sort_order=0, bbox=None, asset_uri=None):
    meta = {}
    if visible_text is not None:
        meta["visible_text"] = visible_text
    if asset_uri is not None:
        meta["asset_uri"] = asset_uri
    return ElementRecord(
        id=str(uuid.uuid4()),
        doc_id="doc",
        page_id="p1",
        page_number=page,
        type=etype,
        content=content,
        bbox=bbox,
        source=source,
        confidence=conf,
        metadata=meta,
        sort_order=sort_order,
    )


# ── dedup ────────────────────────────────────────────────────────────────────

def test_dedupe_collapses_identical_quote_blocks():
    fox = 'FOX NEWS "So far, Norse has helped 500,000+ people with Acne"'
    elements = [
        _elem("Quote graphic with the Fox News logo.", visible_text=fox, sort_order=0,
              bbox=[10, 20, 100, 40], asset_uri="r2://img/fox_a.png", conf=0.92),
        _elem("Quote graphic with the Fox News logo.", visible_text=fox, sort_order=1,
              bbox=[10, 320, 100, 40], asset_uri="r2://img/fox_b.png", conf=0.92),
        _elem("A totally different product photo of a jar.", visible_text="norse organics", sort_order=2),
    ]
    kept, report = dedupe_elements(elements, threshold=0.90)
    assert len(kept) == 2, "the two identical Fox blocks should collapse to one"
    survivor = next(e for e in kept if "Fox News" in e.content)
    assert survivor.metadata["dup_count"] == 2
    assert len(survivor.metadata["duplicate_ids"]) == 1
    assert len(report) == 1

    # Audit snapshot of the dropped duplicate retains location + source details.
    snaps = survivor.metadata["duplicate_snapshots"]
    assert len(snaps) == 1
    s = snaps[0]
    assert s["id"] == survivor.metadata["duplicate_ids"][0]
    assert s["bbox"] == [10, 320, 100, 40]          # the dropped one (sort_order=1)
    assert s["visible_text"] == fox
    assert s["asset_uri"] == "r2://img/fox_b.png"
    assert s["confidence"] == 0.92
    assert s["page_number"] == 1
    assert s["sort_order"] == 1
    assert s["source"] == "visual_understanding"
    assert s["type"] == "text_block"


def test_dedupe_keeps_distinct_and_respects_modality():
    quote = 'GLAMOUR "Ingredient transparency is at the core of Norse Organics"'
    elements = [
        _elem(quote, source="ocr", etype="paragraph"),          # body text
        _elem("logo crop", visible_text=quote, etype="text_block"),  # visual
    ]
    kept, _ = dedupe_elements(elements, threshold=0.90)
    # Same text but different modality (text vs visual) must NOT be merged.
    assert len(kept) == 2


# ── reconcile: Tier A canonicalize ───────────────────────────────────────────

def test_reconcile_canonicalizes_brand_slip():
    elements = [
        _elem("Norse Organics is a skincare brand.", source="ocr", etype="paragraph"),
        _elem("Why Norse Organics works for acne.", source="ocr", etype="heading"),
        _elem("Ingredient transparency at Norse Organics.", source="ocr", etype="paragraph"),
        _elem("product jar", visible_text="horse organics 6-IN-1 DAILY GLOW & MOISTURIZE",
              etype="product_image"),
    ]
    out, conflicts = reconcile_names(
        elements, min_occurrences=3, canonicalize_ratio=3.0, variant_min_ratio=0.80
    )
    slip = out[-1]
    assert "Norse Organics" in slip.metadata["visible_text"], slip.metadata["visible_text"]
    assert "horse organics" not in slip.metadata["visible_text"].lower()
    # A pure brand slip is not a person-name conflict.
    assert conflicts == []


# ── reconcile: Tier B flag (never overwrite) ─────────────────────────────────

def test_reconcile_flags_person_name_conflict_without_overwriting():
    body = _elem("The company was founded by Daniel Hoftun in 2019.",
                 source="native_text", etype="paragraph")
    sig = _elem("Daniel Hoffman", source="visual_understanding", etype="text_block",
                visible_text="Daniel Hoffman")
    out, conflicts = reconcile_names(
        [body, sig], min_occurrences=3, canonicalize_ratio=3.0, variant_min_ratio=0.80
    )
    # Neither spelling overwritten.
    assert "Hoftun" in out[0].content
    assert "Hoffman" in out[1].content
    # Exactly one conflict, both spellings retained.
    assert len(conflicts) == 1
    variants = {v.lower() for v in conflicts[0]["variants"]}
    assert any("hoftun" in v for v in variants)
    assert any("hoffman" in v for v in variants)
    # Both bearing elements carry the flag for the answer layer.
    assert out[0].metadata.get("name_conflict") is not None
    assert out[1].metadata.get("name_conflict") is not None


# ── text_sim + dedup edges ───────────────────────────────────────────────────

def test_text_sim_basics():
    from app.services.processing_v3.text_sim import normalize_text, similarity, edit_ratio
    assert normalize_text("  Norse,  Organics! ") == "norse organics"
    assert similarity("Fox News quote", "fox news quote") == 1.0
    assert similarity("totally different", "nothing alike") < 0.5
    assert edit_ratio("horse organics", "norse organics") > 0.9


def test_dedupe_preserves_unique_and_empty():
    els = [
        _elem(""),            # empty content — always kept, never merged
        _elem("unique A"),
        _elem("unique B"),
    ]
    kept, report = dedupe_elements(els, threshold=0.90)
    assert len(kept) == 3
    assert report == []


def test_reconcile_leaves_clean_docs_untouched():
    els = [
        _elem("Norse Organics is great.", source="ocr", etype="paragraph"),
        _elem("More about Norse Organics.", source="ocr", etype="paragraph"),
    ]
    out, conflicts = reconcile_names(els)
    assert conflicts == []
    assert "Norse Organics" in out[0].content and "Norse Organics" in out[1].content
