"""Tests for MCP _visual_as_image_entry.

Ensures get_file / get_pages / get_section (which return image lists through this
helper) expose the same cleanup/audit fields as list_visuals / get_visual, so a
client doesn't lose dedup/conflict metadata depending on which tool it calls.
"""

from app.services.mcp.tools import _visual_as_image_entry


def _full_visual() -> dict:
    return {
        "element_id": "vis-1",
        "index": 7,
        "page": 2,
        "type": "text_block",
        "asset_type": "review_screenshot",
        "description": "Fox News quote graphic",
        "text_inside": "FOX NEWS ...",
        "asset_uri": "r2://img/fox_a.png",
        "bbox": [10, 20, 100, 40],
        "confidence": 0.92,
        "dup_count": 2,
        "duplicate_snapshots": [{
            "id": "drop", "bbox": [10, 320, 100, 40],
            "asset_uri": "r2://img/fox_b.png", "confidence": 0.92,
            "visible_text": "FOX NEWS ...", "source": "visual_understanding",
        }],
        "name_conflict": {
            "variants": ["Daniel Hoftun", "Daniel Hoffman"],
            "sources": ["native_text", "visual_understanding"],
        },
    }


def test_entry_preserves_audit_and_conflict_fields():
    entry = _visual_as_image_entry(_full_visual())
    assert entry["image_id"] == "vis-1"
    assert entry["asset_uri"] == "r2://img/fox_a.png"
    assert entry["bbox"] == [10, 20, 100, 40]
    assert entry["confidence"] == 0.92
    assert entry["dup_count"] == 2
    assert entry["duplicate_snapshots"][0]["asset_uri"] == "r2://img/fox_b.png"
    assert entry["name_conflict"]["variants"] == ["Daniel Hoftun", "Daniel Hoffman"]
    # page is opt-in
    assert "page" not in entry


def test_entry_include_page():
    entry = _visual_as_image_entry(_full_visual(), include_page=True)
    assert entry["page"] == 2


def test_entry_omits_absent_fields_cleanly():
    minimal = {
        "element_id": "vis-2",
        "index": 1,
        "type": "logo",
        "asset_type": "logo",
        "description": "a logo",
        "text_inside": "",
    }
    entry = _visual_as_image_entry(minimal)
    # Conditional cleanup fields are omitted entirely when absent.
    assert "dup_count" not in entry
    assert "duplicate_snapshots" not in entry
    assert "name_conflict" not in entry
    # Always-present structural fields are None when absent (not missing).
    assert entry["asset_uri"] is None
    assert entry["bbox"] is None
    assert entry["confidence"] is None
