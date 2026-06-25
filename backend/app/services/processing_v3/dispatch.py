"""Central scheduler for document processing.

Every upload path funnels file processing through :func:`schedule_file_processing`
so there is exactly one place that decides *how* a file gets processed:

* **Cloud Tasks worker** (Phase 3) — when ``processing_queue`` and
  ``processing_worker_url`` are configured, each file is enqueued as its own
  Cloud Tasks HTTP task pointing at a dedicated Cloud Run worker. That gives true
  horizontal parallelism (one instance per file), dedicated always-on CPU, and
  scale-to-zero when idle.
* **In-process fan-out** (Phase 2 — the default) — otherwise files are processed
  concurrently inside the current service via ``asyncio`` tasks, bounded by a
  semaphore so a large batch can't exhaust CPU/RAM or the DB pool. Each pipeline
  is mostly network I/O (R2 + Mistral + Voyage + Qdrant), so running several in
  flight compresses the wall-clock dramatically even on a single CPU.

The two backends are interchangeable: switching on Cloud Tasks is purely a
matter of setting the env vars and deploying the worker — no code change.
"""

from __future__ import annotations

import asyncio
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Bound concurrent in-process pipelines. Strong refs to live tasks are kept so the
# event loop does not garbage-collect a still-running background task.
_semaphore: asyncio.Semaphore | None = None
_inflight: set[asyncio.Task] = set()


def _get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(settings.file_processing_concurrency)
    return _semaphore


def cloud_tasks_enabled() -> bool:
    return bool(
        settings.processing_queue
        and settings.processing_worker_url
        and settings.processing_secret
        and settings.gcp_project
    )


async def _run_guarded(file_id: str, trace_run_id: str | None, source: str) -> None:
    from app.services.processing_v3.orchestrator import process_file

    async with _get_semaphore():
        try:
            await process_file(file_id, trace_run_id, source)
        except Exception:  # pragma: no cover - process_file already logs + marks failed
            logger.exception("[dispatch] in-process pipeline crashed for file %s", file_id)


def _spawn_inprocess(file_id: str, trace_run_id: str | None, source: str) -> None:
    task = asyncio.create_task(_run_guarded(file_id, trace_run_id, source))
    _inflight.add(task)
    task.add_done_callback(_inflight.discard)


async def _enqueue_cloud_task(file_id: str, trace_run_id: str | None, source: str) -> bool:
    """Enqueue one HTTP task to the processing worker. Returns False on failure
    so the caller can fall back to in-process execution."""

    def _enqueue() -> None:
        from google.cloud import tasks_v2

        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(
            settings.gcp_project, settings.gcp_region, settings.processing_queue
        )
        url = f"{settings.processing_worker_url.rstrip('/')}/v1/internal/process-file"
        body = json.dumps(
            {"file_id": file_id, "trace_run_id": trace_run_id, "source": source}
        ).encode()
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": {
                    "Content-Type": "application/json",
                    "X-Processing-Secret": settings.processing_secret,
                },
                "body": body,
            },
            # Dedupe: a retried upload of the same file collapses to one task while
            # the previous one is still in the queue.
            "name": f"{parent}/tasks/file-{file_id}",
        }
        client.create_task(request={"parent": parent, "task": task})

    try:
        await asyncio.to_thread(_enqueue)
        logger.info("[dispatch] enqueued Cloud Task for file %s", file_id)
        return True
    except Exception as exc:
        # AlreadyExists means an identical task is already queued — that is success.
        if exc.__class__.__name__ == "AlreadyExists":
            logger.info("[dispatch] Cloud Task already queued for file %s", file_id)
            return True
        logger.warning(
            "[dispatch] Cloud Tasks enqueue failed for file %s, falling back in-process: %s",
            file_id, exc,
        )
        return False


async def schedule_file_processing(
    file_id: str, trace_run_id: str | None = None, source: str = "upload"
) -> None:
    """Schedule one file for processing. Returns immediately; processing happens
    out-of-band (Cloud Tasks worker, or an in-process background task)."""
    if cloud_tasks_enabled() and await _enqueue_cloud_task(file_id, trace_run_id, source):
        return
    _spawn_inprocess(file_id, trace_run_id, source)
