"""
Regression tests for the query() guards (count routing + semantic/structural split).

These lock in the deterministic behaviour:
  • structural count questions → exact metric list (incl. multi-count)
  • semantic nouns (languages, ingredients, products, claims, emails,
    addresses, testimonials) are NEVER treated as a metadata count
  • container references ("how many images IN THE DOCUMENT") don't get
    misread as also asking for a document/file count

The value-level checks the plan lists (images→58, sections→26, the multi-count
1/26/58/21/79/1, "organic food items" not relabeled, subscription only-explicit,
Japanese absence, support email) depend on live data and/or the LLM, so they are
verified against the live MCP bucket rather than unit-tested here — the prompt is
kept generic and never hardcodes any specific question's answer.
"""
from __future__ import annotations

import pytest

from app.services.agent.service import _detect_count_intents


@pytest.mark.parametrize(
    "question,expected",
    [
        # single structural counts
        ("How many images are in the document?", ["images"]),
        ("How many sections are in the document?", ["sections"]),
        ("How many pages does it have?", ["pages"]),
        ("How many chunks does the file have?", ["chunks"]),
        ("How many text blocks are there?", ["text_blocks"]),
        ("How many visuals are in the file?", ["total_visuals"]),
        ("How many documents are in the bucket?", ["files"]),
        # multi-count: must return ALL requested metrics, not stop at the first
        (
            "How many pages, sections, images, text blocks, total visuals, and files "
            "are in this bucket?",
            ["files", "pages", "sections", "images", "text_blocks", "total_visuals"],
        ),
        # container reference must not add a spurious file/document count
        ("How many figures appear in this document?", ["images"]),
        ("How many images on page 3?", ["images"]),
        # SEMANTIC nouns: never a metadata count — must fall through to retrieval
        ("How many languages are mentioned?", []),
        ("How many ingredients are listed?", []),
        ("How many products are offered?", []),
        ("How many claims does it make?", []),
        ("How many emails are shown?", []),
        ("How many addresses are listed?", []),
        ("How many testimonials are there?", []),
        # not a count question at all
        ("What is the refund policy?", []),
        ("Tell me about arctic plants.", []),
    ],
)
def test_detect_count_intents(question, expected):
    assert sorted(_detect_count_intents(question)) == sorted(expected)


def test_multi_count_preserves_canonical_order():
    """Multi-count returns metrics in canonical (definition) order regardless of
    the order they appear in the question."""
    got = _detect_count_intents(
        "How many files, images and pages are here?"
    )
    # canonical order is files, pages, sections, images, text_blocks, total_visuals, chunks
    assert got == ["files", "pages", "images"]


def test_languages_is_not_files():
    """The exact regression from the plan: a 'how many languages' question must
    not be answered as a file count."""
    assert "files" not in _detect_count_intents("How many languages are mentioned?")
    assert _detect_count_intents("How many languages are mentioned?") == []
