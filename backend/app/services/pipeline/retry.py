"""Async retry decorator and PipelineError for the file processing pipeline."""

import asyncio
import functools
import logging
import traceback
from typing import Any, Callable, Coroutine, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])

MAX_RETRIES = 3
RETRY_DELAY = 3  # seconds


class PipelineError(Exception):
    """Raised when a pipeline stage fails after all retries are exhausted."""

    def __init__(self, stage: str, cause: Exception):
        self.stage = stage
        self.cause = cause
        super().__init__(f"Pipeline stage '{stage}' failed after {MAX_RETRIES} attempts: {cause}")


def with_retry(stage: str):
    """
    Decorator factory.  Usage:

        @with_retry("docling_extraction")
        async def run_docling(...):
            ...

    Retries up to MAX_RETRIES times with RETRY_DELAY seconds between attempts.
    Raises PipelineError if all attempts fail.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    logger.warning(
                        "[%s] attempt %d/%d failed: %s",
                        stage,
                        attempt,
                        MAX_RETRIES,
                        exc,
                    )
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(RETRY_DELAY)
                    else:
                        logger.error(
                            "[%s] all %d attempts exhausted. Last error:\n%s",
                            stage,
                            MAX_RETRIES,
                            traceback.format_exc(),
                        )
            raise PipelineError(stage, last_exc)
        return wrapper  # type: ignore[return-value]
    return decorator
