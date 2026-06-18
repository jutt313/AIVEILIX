from __future__ import annotations

import logging
import re

try:
    import colorlog as _colorlog
    _HAS_COLORLOG = True
except ImportError:  # pragma: no cover
    _colorlog = None  # type: ignore[assignment]
    _HAS_COLORLOG = False


# ANSI colors applied to [TAG] prefixes in agent log lines
_TAG_COLORS: dict[str, str] = {
    "USER":    "\033[94m",   # bright blue   — incoming user message
    "MEMORY":  "\033[96m",   # cyan          — conversation memory search
    "SEARCH":  "\033[93m",   # bright yellow — bucket document search
    "WEB":     "\033[33m",   # yellow        — web search
    "FETCH":   "\033[36m",   # teal          — URL fetch
    "LLM":     "\033[95m",   # magenta       — LLM call
    "ANSWER":  "\033[92m",   # bright green  — final answer generated
    "RERANK":  "\033[35m",   # purple        — reranker
    "STEP":    "\033[37m",   # light grey    — misc agent step
}
_RESET = "\033[0m"
_TAG_RE = re.compile(r"\[([A-Z]+)\]")


def _colorize_tags(text: str, raw_message: str) -> str:
    """Replace [TAG] occurrences in *text* using colors from _TAG_COLORS."""
    for match in _TAG_RE.finditer(raw_message):
        tag = match.group(1)
        color = _TAG_COLORS.get(tag)
        if color:
            text = text.replace(f"[{tag}]", f"{color}[{tag}]{_RESET}", 1)
    return text


if _HAS_COLORLOG:
    class _Formatter(_colorlog.ColoredFormatter):  # type: ignore[misc]
        def format(self, record: logging.LogRecord) -> str:
            return _colorize_tags(super().format(record), record.getMessage())
else:
    class _Formatter(logging.Formatter):  # type: ignore[no-redef]
        def format(self, record: logging.LogRecord) -> str:
            return super().format(record)


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level)
    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler()

    if _HAS_COLORLOG:
        handler.setFormatter(
            _Formatter(
                "%(log_color)s%(levelname)-8s%(reset)s  "
                "%(cyan)s%(name)-40s%(reset)s  "
                "%(message)s",
                log_colors={
                    "DEBUG":    "white",
                    "INFO":     "bold_green",
                    "WARNING":  "bold_yellow",
                    "ERROR":    "bold_red",
                    "CRITICAL": "bold_white,bg_red",
                },
                reset=True,
            )
        )
    else:
        handler.setFormatter(
            logging.Formatter("%(levelname)-8s  %(name)-40s  %(message)s")
        )

    root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in (
        "httpx", "httpcore", "hpack", "h2",
        "uvicorn.access",
        "sqlalchemy.engine", "sqlalchemy.pool",
        "openai._base_client", "anthropic._base_client",
        "qdrant_client", "grpc",
        "llama_index", "llama_index.core",
        "docling", "docling_core",
        "torch", "torchvision",
        "transformers", "sentence_transformers",
        "FlagEmbedding", "open_clip",
        "PIL",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)
