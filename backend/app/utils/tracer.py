"""
Request-level step tracer for detailed endpoint diagnostics.

Usage:
    t = Tracer("POST /api/buckets/{id}/chat", user_id=user_id)
    t.step("Fetching files from DB")
    ...do work...
    t.step("Generating embeddings")  # auto-logs time since last step
    ...do work...
    t.done()  # logs total time + summary
"""
import time
import logging
import uuid

logger = logging.getLogger("tracer")


class Tracer:
    def __init__(self, endpoint: str, **tags):
        self.id = str(uuid.uuid4())[:8]
        self.endpoint = endpoint
        self.tags = tags
        self._t0 = time.perf_counter()
        self._last = self._t0
        self._steps: list[dict] = []
        self._failed = False

        tag_str = " ".join(f"{k}={v}" for k, v in tags.items() if v)
        logger.info(f"[{self.id}] START {endpoint}  {tag_str}")

    def step(self, label: str, **extra):
        """Log a step with elapsed time since last step."""
        now = time.perf_counter()
        ms = round((now - self._last) * 1000, 1)
        total_ms = round((now - self._t0) * 1000, 1)
        self._last = now

        entry = {"label": label, "ms": ms, "total_ms": total_ms, **extra}
        self._steps.append(entry)

        extra_str = " ".join(f"{k}={v}" for k, v in extra.items()) if extra else ""
        speed = _speed(ms)
        logger.info(f"[{self.id}]   {speed} {label}  {ms}ms (total {total_ms}ms)  {extra_str}")

    def error(self, label: str, exc: Exception = None):
        """Log an error step."""
        now = time.perf_counter()
        ms = round((now - self._last) * 1000, 1)
        total_ms = round((now - self._t0) * 1000, 1)
        self._last = now
        self._failed = True

        err_msg = str(exc)[:200] if exc else ""
        self._steps.append({"label": label, "ms": ms, "total_ms": total_ms, "error": err_msg})
        logger.error(f"[{self.id}]   FAIL {label}  {ms}ms (total {total_ms}ms)  err={err_msg}")

    def done(self, status_code: int = 200):
        """Log completion with full summary."""
        total_ms = round((time.perf_counter() - self._t0) * 1000, 1)
        speed = _speed(total_ms)
        status = "FAIL" if self._failed else "OK"

        # Find slowest step
        slowest = max(self._steps, key=lambda s: s["ms"]) if self._steps else None
        slowest_str = f"  slowest={slowest['label']}({slowest['ms']}ms)" if slowest else ""

        logger.info(
            f"[{self.id}] END {self.endpoint}  {status} {status_code}  "
            f"{total_ms}ms  {speed}  steps={len(self._steps)}{slowest_str}"
        )

        # If very slow, dump all steps as a summary
        if total_ms >= 3000:
            summary = " -> ".join(f"{s['label']}({s['ms']}ms)" for s in self._steps)
            logger.warning(f"[{self.id}] SLOW TRACE: {summary}")

        return total_ms


def _speed(ms: float) -> str:
    if ms >= 5000:
        return "🔴"
    elif ms >= 1000:
        return "🟡"
    else:
        return "🟢"
