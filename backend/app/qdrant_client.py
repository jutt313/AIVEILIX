"""Qdrant client construction from settings (embedded path vs remote host/port)."""

import logging
import socket
import warnings
from pathlib import Path
from urllib.parse import urlparse

from qdrant_client import QdrantClient
from qdrant_client.async_qdrant_client import AsyncQdrantClient

from app.config import settings

logger = logging.getLogger(__name__)

_sync_client: QdrantClient | None = None
_async_client: AsyncQdrantClient | None = None
_QDRANT_CLOSE_WARNING_RE = r"Unable to close (?:http connection|grpc_channel)\. Connection was interrupted on the server side"


def _local_path() -> str | None:
    p = settings.qdrant_path
    if p is None:
        return None
    s = p.strip()
    return s or None


def _cloud_url() -> str | None:
    u = (settings.qdrant_url or "").strip()
    return u or None


def _default_local_path() -> str | None:
    path = Path(__file__).resolve().parent.parent / "database" / "qdrant" / "data" / "local"
    return str(path) if path.exists() else None


def _cloud_url_resolves(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        return False
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError:
        return False
    return True


def _resolved_target() -> dict[str, str | None]:
    url = _cloud_url()
    path = _local_path()

    if url:
        if _cloud_url_resolves(url):
            return {"mode": "cloud", "target": url, "fallback_from": None}
        auto_local = _default_local_path()
        if settings.app_env == "development" and path is None and auto_local is not None:
            return {"mode": "local", "target": auto_local, "fallback_from": url}
        return {"mode": "cloud", "target": url, "fallback_from": None}

    if path:
        return {"mode": "local", "target": path, "fallback_from": None}

    return {
        "mode": "remote",
        "target": f"{settings.qdrant_host}:{settings.qdrant_port}",
        "fallback_from": None,
    }


def get_qdrant_client() -> QdrantClient:
    global _sync_client
    if _sync_client is None:
        target = _resolved_target()
        if target["fallback_from"]:
            logger.warning(
                "Qdrant cloud host was not resolvable, using embedded local store at %s",
                target["target"],
            )
        if target["mode"] == "cloud":
            _sync_client = QdrantClient(url=target["target"], api_key=settings.qdrant_api_key or None)
        elif target["mode"] == "local":
            _sync_client = QdrantClient(path=target["target"])
        else:
            _sync_client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    return _sync_client


def get_async_qdrant_client() -> AsyncQdrantClient:
    global _async_client
    if _async_client is None:
        target = _resolved_target()
        if target["fallback_from"]:
            logger.warning(
                "Qdrant cloud host was not resolvable, using embedded local store at %s",
                target["target"],
            )
        if target["mode"] == "cloud":
            _async_client = AsyncQdrantClient(url=target["target"], api_key=settings.qdrant_api_key or None)
        elif target["mode"] == "local":
            _async_client = AsyncQdrantClient(path=target["target"])
        else:
            _async_client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    return _async_client


async def check_qdrant_connection() -> dict[str, object]:
    target = _resolved_target()
    client = get_async_qdrant_client()
    collections = await client.get_collections()
    report = {
        "status": "ok",
        "mode": target["mode"],
        "target": target["target"],
        "collections": [collection.name for collection in collections.collections],
    }
    if target["fallback_from"]:
        report["fallback_from"] = target["fallback_from"]
    return report


async def close_qdrant_clients() -> None:
    global _sync_client, _async_client

    if _async_client is not None:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=_QDRANT_CLOSE_WARNING_RE,
                category=UserWarning,
            )
            await _async_client.close()
        _async_client = None

    if _sync_client is not None:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=_QDRANT_CLOSE_WARNING_RE,
                category=UserWarning,
            )
            _sync_client.close()
        _sync_client = None
