"""
Step 07c — name reconciliation for pipeline v3.

Proper names enter from two engines that disagree:
  * body text  → native_text (PyMuPDF) / ocr (Mistral)
  * in-image text (logos, product labels, signatures) → visual_understanding

So the same brand reads "norse organics" on most of the page but "horse
organics" on one product crop, and the founder is "Daniel Hoftun" in the body
yet "Daniel Hoffman" in the signature image.

This pass runs in the orchestrator on the RAW merged elements, BEFORE the
summary is generated — deliberately, so the summary (and everything downstream)
is built from reconciled text and the summary is never used as the source of
truth (it is itself generated from the dirty data).

Two tiers, per the agreed policy:
  * Tier A — canonicalize: a high-frequency dominant spelling absorbs an obvious
    rare OCR slip (horse organics -> Norse Organics). Gated hard on frequency so
    it never fires on one-off names.
  * Tier B — flag, never overwrite: low-frequency / ambiguous proper nouns that
    disagree across sources (Hoftun vs Hoffman) are kept BOTH ways and stamped
    with ``metadata["name_conflict"]`` so the answer layer can surface the
    discrepancy instead of silently picking one.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass, field

from app.services.processing_v3.layout import ElementRecord
from app.services.processing_v3.text_sim import edit_ratio, normalize_text

logger = logging.getLogger(__name__)

# Runs of Capitalized words — captures person + brand names where they appear
# title-cased ("Daniel Hoffman", "Norse Organics", "Fox News").
_PROPER_RE = re.compile(r"\b[A-Z][A-Za-z'’&]+(?:\s+[A-Z][A-Za-z'’&]+){0,3}\b")

_MIN_WORDS = 2   # person/brand names are multi-word; single tokens are too noisy
_MAX_WORDS = 4
_MIN_NORM_LEN = 5


@dataclass
class _Entity:
    surface: Counter = field(default_factory=Counter)  # surface form -> count
    sources: set[str] = field(default_factory=set)
    titlecase_count: int = 0
    count: int = 0  # true frequency incl. any-case occurrences

    def best_surface(self) -> str:
        return self.surface.most_common(1)[0][0] if self.surface else ""


def _compare_text(elem: ElementRecord) -> str:
    # Join with " | " (not a space): a non-word separator stops the proper-noun
    # regex from running a name at the end of `content` into an identical name at
    # the start of `visible_text`, while normalize_text() drops it for matching.
    meta = elem.metadata or {}
    parts = [elem.content or ""]
    vis = meta.get("visible_text")
    if vis:
        parts.append(str(vis))
    return " | ".join(p for p in parts if p).strip()


def _extract_entities(elements: list[ElementRecord]) -> dict[str, _Entity]:
    entities: dict[str, _Entity] = {}
    for elem in elements:
        text = _compare_text(elem)
        for m in _PROPER_RE.finditer(text):
            phrase = m.group(0).strip()
            wc = len(phrase.split())
            if wc < _MIN_WORDS or wc > _MAX_WORDS:
                continue
            norm = normalize_text(phrase)
            if len(norm) < _MIN_NORM_LEN:
                continue
            ent = entities.setdefault(norm, _Entity())
            ent.surface[phrase] += 1
            ent.sources.add(elem.source)
            ent.titlecase_count += 1
    return entities


def _count_true_frequency(
    entities: dict[str, _Entity], norm_words: list[list[str]]
) -> None:
    """True frequency including lowercase occurrences (e.g. 'norse organics' in
    a product label) so brand names clear the canonicalization gate."""
    for norm, ent in entities.items():
        nw = norm.split()
        k = len(nw)
        c = 0
        for words in norm_words:
            for s in range(0, len(words) - k + 1):
                if words[s:s + k] == nw:
                    c += 1
        ent.count = max(c, ent.titlecase_count)


def _cluster_entities(
    entities: dict[str, _Entity], variant_min_ratio: float
) -> list[list[str]]:
    """Group entity norms that are spelling variants of one another."""
    norms = list(entities.keys())
    clusters: list[list[str]] = []
    assigned: set[str] = set()
    for i, a in enumerate(norms):
        if a in assigned:
            continue
        group = [a]
        assigned.add(a)
        for b in norms[i + 1:]:
            if b in assigned:
                continue
            if _same_entity(a, b, variant_min_ratio):
                group.append(b)
                assigned.add(b)
        clusters.append(group)
    return clusters


def _same_entity(a: str, b: str, variant_min_ratio: float) -> bool:
    """Two normalized phrases are variants of the same entity if they're close
    overall, OR same word-count with exactly one differing (similar) word."""
    if edit_ratio(a, b) >= variant_min_ratio:
        return True
    wa, wb = a.split(), b.split()
    if len(wa) == len(wb) and len(wa) >= 2:
        diff = [(x, y) for x, y in zip(wa, wb) if x != y]
        if len(diff) == 1 and edit_ratio(diff[0][0], diff[0][1]) >= 0.6:
            return True
    return False


def _replace_in_text(
    text: str,
    entity_norm: str,
    canon_surface: str,
    variant_min_ratio: float,
    skip_norms: set[str],
) -> tuple[str, int]:
    """Replace rare near-miss windows of a frequent entity with its canonical
    surface form. Leaves exact matches and other known entities untouched."""
    words = text.split()
    k = len(entity_norm.split())
    if k == 0 or len(words) < k:
        return text, 0
    out: list[str] = []
    i = 0
    applied = 0
    while i < len(words):
        window_norm = normalize_text(" ".join(words[i:i + k]))
        if (
            window_norm
            and window_norm != entity_norm
            and window_norm not in skip_norms
            and edit_ratio(window_norm, entity_norm) >= variant_min_ratio
        ):
            out.append(canon_surface)
            i += k
            applied += 1
        else:
            out.append(words[i])
            i += 1
    return " ".join(out), applied


def _apply_canonicalization(
    elem: ElementRecord,
    entity_norm: str,
    canon_surface: str,
    variant_min_ratio: float,
    skip_norms: set[str],
) -> int:
    applied = 0
    new_content, n1 = _replace_in_text(
        elem.content or "", entity_norm, canon_surface, variant_min_ratio, skip_norms
    )
    if n1:
        elem.content = new_content
        applied += n1
    meta = elem.metadata or {}
    if meta.get("visible_text"):
        new_vis, n2 = _replace_in_text(
            str(meta["visible_text"]), entity_norm, canon_surface, variant_min_ratio, skip_norms
        )
        if n2:
            elem.metadata = {**meta, "visible_text": new_vis}
            applied += n2
    return applied


def _phrase_in_words(words: list[str], phrase_norm: str) -> bool:
    pw = phrase_norm.split()
    k = len(pw)
    return any(words[s:s + k] == pw for s in range(0, len(words) - k + 1))


def reconcile_names(
    elements: list[ElementRecord],
    *,
    min_occurrences: int = 3,
    canonicalize_ratio: float = 3.0,
    variant_min_ratio: float = 0.80,
) -> tuple[list[ElementRecord], list[dict]]:
    """Reconcile proper-name spellings across elements.

    Returns (elements, conflicts) where conflicts is a doc-level list of
    ``{"variants": [...], "sources": [...]}`` for the answer layer to surface.
    Mutates element content (Tier A) and metadata (Tier B) in place.
    """
    if not elements:
        return elements, []

    entities = _extract_entities(elements)
    if not entities:
        return elements, []

    norm_words = [normalize_text(_compare_text(e)).split() for e in elements]
    _count_true_frequency(entities, norm_words)

    clusters = _cluster_entities(entities, variant_min_ratio)

    conflicts: list[dict] = []
    conflict_norms: set[str] = set()
    for cluster in clusters:
        if len(cluster) < 2:
            continue
        ordered = sorted(cluster, key=lambda n: entities[n].count, reverse=True)
        top, second = ordered[0], ordered[1]
        dominant = (
            entities[top].count >= min_occurrences
            and entities[top].count >= canonicalize_ratio * max(1, entities[second].count)
        )
        if dominant:
            # Top is a frequent entity; the window pass below will absorb the
            # rarer title-cased variants too. Nothing to flag.
            continue
        # Tier B — ambiguous: keep all spellings, flag the conflict.
        variants = [entities[n].best_surface() for n in ordered]
        sources = sorted({s for n in cluster for s in entities[n].sources})
        conflicts.append({"variants": variants, "sources": sources})
        conflict_norms.update(cluster)

    # Tier A — canonicalize rare near-misses of frequent entities (catches the
    # lowercase 'horse organics' that never appears title-cased).
    all_entity_norms = set(entities.keys())
    frequent = [
        n for n, ent in entities.items()
        if ent.count >= min_occurrences and n not in conflict_norms
    ]
    rewrites = 0
    for norm in frequent:
        canon = entities[norm].best_surface()
        # Don't rewrite OTHER real entities or any flagged conflict variant.
        skip = (all_entity_norms - {norm}) | conflict_norms
        for elem in elements:
            rewrites += _apply_canonicalization(
                elem, norm, canon, variant_min_ratio, skip
            )

    # Stamp Tier B conflicts onto every element that bears a conflicting spelling.
    if conflicts:
        for elem, words in zip(elements, norm_words):
            for conf in conflicts:
                if any(_phrase_in_words(words, normalize_text(v)) for v in conf["variants"]):
                    elem.metadata = {
                        **(elem.metadata or {}),
                        "name_conflict": {
                            "variants": conf["variants"],
                            "sources": conf["sources"],
                        },
                    }
                    break

    if rewrites or conflicts:
        logger.info(
            "reconcile_names rewrites=%s conflicts=%s sample_conflict=%s",
            rewrites, len(conflicts), conflicts[0] if conflicts else None,
        )
    return elements, conflicts
