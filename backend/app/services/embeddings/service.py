from __future__ import annotations

import hashlib
import logging
import math
import re
from functools import lru_cache
from pathlib import Path

try:
    import tiktoken
except Exception:  # pragma: no cover - optional runtime dependency
    tiktoken = None

try:
    from FlagEmbedding import BGEM3FlagModel
except Exception:  # pragma: no cover - import can fail in limited runtimes
    BGEM3FlagModel = None

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_DIMENSION = 1024
_WORD_RE = re.compile(r"[a-zA-Z0-9']+")


def _load_tokenizer():
    if tiktoken is None:
        return None
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception as exc:
        logger.warning("Falling back to heuristic token counting because tiktoken is unavailable: %s", exc)
        return None


_TOKENIZER = _load_tokenizer()


def estimate_token_count(text: str) -> int:
    if not text:
        return 0
    if _TOKENIZER is not None:
        return len(_TOKENIZER.encode(text))
    return max(1, int(len(text.split()) * 1.3))


def split_text_for_memory(text: str, chunk_size: int = 256, overlap: int = 50) -> list[str]:
    if _TOKENIZER is not None:
        tokens = _TOKENIZER.encode(text or "")
        if not tokens:
            return []

        chunks: list[str] = []
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunks.append(_TOKENIZER.decode(tokens[start:end]).strip())
            if end >= len(tokens):
                break
            start = max(end - overlap, start + 1)

        return [chunk for chunk in chunks if chunk]

    words = (text or "").split()
    if not words:
        return []

    words_per_chunk = max(1, int(chunk_size / 1.3))
    overlap_words = max(0, int(overlap / 1.3))
    step = max(1, words_per_chunk - overlap_words)
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + words_per_chunk, len(words))
        chunks.append(" ".join(words[start:end]).strip())
        if end >= len(words):
            break
        start += step
    return [chunk for chunk in chunks if chunk]


def normalize_terms(text: str) -> list[str]:
    stop_words = {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
        "i", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
        "was", "what", "when", "where", "which", "who", "why", "with", "you",
    }
    terms = [term.lower() for term in _WORD_RE.findall(text)]
    return [term for term in terms if term not in stop_words and len(term) > 1]


def _hash_embedding(text: str, dimension: int = DEFAULT_EMBEDDING_DIMENSION) -> list[float]:
    vector = [0.0] * dimension
    for term in normalize_terms(text):
        digest = hashlib.blake2b(term.encode("utf-8"), digest_size=16).digest()
        idx = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[idx] += sign

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


@lru_cache(maxsize=1)
def _load_bge_model():
    if BGEM3FlagModel is None:
        return None
    cache_root = Path.home() / ".cache" / "huggingface" / "hub" / "models--BAAI--bge-m3"
    if not cache_root.exists():
        logger.info("BGE-M3 cache not found locally; using hash-based embeddings fallback")
        return None
    try:
        return BGEM3FlagModel("BAAI/bge-m3", use_fp16=False)
    except Exception:
        return None


def can_use_semantic_embeddings() -> bool:
    return _load_bge_model() is not None


def embedding_dimension() -> int:
    model = _load_bge_model()
    if model is None:
        return DEFAULT_EMBEDDING_DIMENSION

    try:
        sample = model.encode(["health check"], return_dense=True)
        dense = sample.get("dense_vecs") or []
        if dense:
            return len(dense[0])
    except Exception:
        pass

    return DEFAULT_EMBEDDING_DIMENSION


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _load_bge_model()
    if model is None:
        return [_hash_embedding(text) for text in texts]

    try:
        encoded = model.encode(texts, return_dense=True)
        return [list(vector) for vector in encoded["dense_vecs"]]
    except Exception:
        return [_hash_embedding(text) for text in texts]
