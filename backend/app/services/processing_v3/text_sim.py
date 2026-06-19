"""
Shared text-normalization + similarity helpers for pipeline v3.

Used by:
  * dedup.py           — collapse near-identical elements at ingestion
  * reconcile.py       — group + canonicalize proper-noun spelling variants
  * agent/reranker.py  — content dedup at retrieval time

Kept dependency-free (stdlib only) so it is cheap to import in both the hot
ingestion path and the retrieval path.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)


def normalize_text(text: str) -> str:
    """Lowercase, strip accents + punctuation, collapse whitespace.

    Produces a canonical form for equality/similarity comparison only — never
    for storage or display.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = _PUNCT_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text)
    return text.strip()


def similarity(a: str, b: str) -> float:
    """Similarity in [0, 1] between two raw strings, after normalization.

    Blends a character sequence ratio with token-set Jaccard and takes the
    max — Jaccard is robust to reordering and minor OCR insertions, while the
    sequence ratio catches short near-identical strings. Returns 1.0 on an
    exact normalized match, 0.0 when either side is empty.
    """
    na, nb = normalize_text(a), normalize_text(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    seq = SequenceMatcher(None, na, nb).ratio()
    ta, tb = set(na.split()), set(nb.split())
    if ta and tb:
        jac = len(ta & tb) / len(ta | tb)
        return max(seq, jac)
    return seq


def edit_ratio(a: str, b: str) -> float:
    """Character-level similarity ratio for short tokens / single names.

    Used by name reconciliation to tell a tiny OCR slip ('horse' vs 'norse')
    from genuinely different words.
    """
    na, nb = normalize_text(a), normalize_text(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def bucket_key(text: str, width: int = 16) -> str:
    """Cheap blocking key so fuzzy dedup stays ~O(n) instead of O(n^2).

    Near-identical strings share a prefix of their normalized form, so
    comparing only within the same bucket avoids the full pairwise blowup.
    Exact-duplicate detection should be done separately (keyed on the full
    normalized string) so reordered-but-identical text is still caught.
    """
    return normalize_text(text)[:width]
