"""
Processing Commentary Service
Generates natural, conversational AI commentary during file processing.
Streams to frontend via SSE - no DB writes, no polling.
"""

import asyncio
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# Global: bucket_id -> asyncio.Queue for broadcasting to SSE clients
_broadcast_queues: Dict[str, asyncio.Queue] = {}


def get_or_create_queue(bucket_id: str) -> asyncio.Queue:
    if bucket_id not in _broadcast_queues:
        _broadcast_queues[bucket_id] = asyncio.Queue()
    return _broadcast_queues[bucket_id]


def remove_queue(bucket_id: str):
    _broadcast_queues.pop(bucket_id, None)


def _commentary_for_stage(
    stage: str,
    filename: str,
    meta: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Return a natural language sentence for what the AI is doing right now."""
    meta = meta or {}
    name = filename or "this file"
    page_count = meta.get("page_count")
    image_count = meta.get("image_count", 0)
    chunk_count = meta.get("chunks_count", 0)
    word_count = meta.get("word_count", 0)
    file_type = meta.get("file_type", "")

    if stage == "queued":
        return f"Got {name}, getting ready to take a look..."

    if stage == "uploading":
        return f"Uploading {name}..."

    if stage == "extract_text":
        if file_type in ("jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"):
            return f"Looking at this image carefully — reading what's in it..."
        if file_type == "pdf":
            pages = f"{page_count} pages" if page_count else "pages"
            return f"Opening the PDF, going through {pages}..."
        if file_type in ("py", "js", "ts", "jsx", "tsx", "java", "cpp", "c", "go", "rs"):
            return f"Reading through the code, line by line..."
        return f"Reading through {name}..."

    if stage == "extract_images":
        count = image_count or "some"
        return f"Found {count} image{'s' if image_count != 1 else ''} inside — taking a closer look at each one..."

    if stage == "chunking":
        if word_count > 5000:
            return f"This is a long one — breaking it into sections to understand it better..."
        return f"Splitting the content into pieces I can work with..."

    if stage == "embedding":
        if chunk_count > 50:
            return f"Going through {chunk_count} sections, understanding what each part means..."
        elif chunk_count > 10:
            return f"Working through {chunk_count} sections now..."
        else:
            return f"Understanding the content, almost there..."

    if stage == "summarizing":
        return f"Putting it all together — figuring out what this is really about..."

    if stage == "finalizing":
        return f"Wrapping up, nearly ready..."

    if stage == "ready":
        return None  # Signal to clear the commentary

    if stage == "failed":
        return f"Ran into a problem with {name}."

    return None


def _humanize_progress_label(stage: str, label: Optional[str], current: int, total: int, meta: Optional[Dict[str, Any]] = None) -> Optional[str]:
    meta = meta or {}
    clean_label = (label or "").strip()

    # Use grounded Gemini observation when available.
    vision_hint = str(meta.get("vision_hint") or "").strip()
    if stage == "image_ocr" and vision_hint:
        if total > 0:
            return f"Image {current}/{total}: {vision_hint}"
        return f"I can see: {vision_hint}"

    # Hide implementation details from user-facing commentary.
    if stage == "embedding":
        if total > 0:
            return f"Connecting insights ({current}/{total})..."
        return "Connecting insights..."
    if stage == "chunking":
        return "Organizing sections so I can reason through them..."
    if stage == "storing":
        if total > 0:
            return f"Saving findings ({current}/{total})..."
        return "Saving findings..."

    if clean_label:
        return clean_label
    return _commentary_for_stage(stage, str(meta.get("file_name") or "this file"), meta)


def broadcast_progress(
    bucket_id: str,
    stage: str,
    filename: str,
    file_id: str,
    label: Optional[str],
    current: int,
    total: int,
    meta: Optional[Dict[str, Any]] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
):
    """
    Broadcast throttled, user-safe investigation progress to SSE subscribers.
    """
    text = _humanize_progress_label(stage, label, current, total, meta)
    if not text:
        return

    msg: Dict[str, Any] = {
        "file_id": file_id,
        "stage": stage,
        "text": text,
        "type": "complete" if stage == "ready" else ("error" if stage == "failed" else "update"),
        "current": int(current or 0),
        "total": int(total or 0),
    }

    try:
        queue = get_or_create_queue(bucket_id)
        if loop and loop.is_running():
            asyncio.run_coroutine_threadsafe(queue.put(msg), loop)
        else:
            try:
                running_loop = asyncio.get_event_loop()
                if running_loop.is_running():
                    asyncio.run_coroutine_threadsafe(queue.put(msg), running_loop)
            except RuntimeError:
                pass
    except Exception as e:
        logger.debug(f"Progress broadcast skipped for {bucket_id}: {e}")


def broadcast_stage(
    bucket_id: str,
    stage: str,
    filename: str,
    file_id: str,
    meta: Optional[Dict[str, Any]] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
):
    """
    Called from the sync background processing thread.
    Pushes a commentary message into the bucket's broadcast queue.
    """
    stage_text = _commentary_for_stage(stage, filename, meta)
    broadcast_progress(
        bucket_id=bucket_id,
        stage=stage,
        filename=filename,
        file_id=file_id,
        label=stage_text,
        current=0,
        total=0,
        meta=meta,
        loop=loop,
    )
