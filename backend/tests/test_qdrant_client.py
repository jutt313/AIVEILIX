from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import qdrant_client
from app.services.health import get_dependency_health_report


@pytest.fixture(autouse=True)
def reset_qdrant_clients():
    qdrant_client._sync_client = None
    qdrant_client._async_client = None
    yield
    qdrant_client._sync_client = None
    qdrant_client._async_client = None


def test_resolved_target_falls_back_to_embedded_local_in_development(monkeypatch):
    monkeypatch.setattr(qdrant_client.settings, "app_env", "development")
    monkeypatch.setattr(qdrant_client.settings, "qdrant_url", "https://unresolvable.qdrant.example")
    monkeypatch.setattr(qdrant_client.settings, "qdrant_path", None)
    monkeypatch.setattr(qdrant_client, "_cloud_url_resolves", lambda url: False)
    monkeypatch.setattr(qdrant_client, "_default_local_path", lambda: "/tmp/qdrant-local")

    target = qdrant_client._resolved_target()

    assert target == {
        "mode": "local",
        "target": "/tmp/qdrant-local",
        "fallback_from": "https://unresolvable.qdrant.example",
    }


def test_resolved_target_keeps_cloud_in_production(monkeypatch):
    monkeypatch.setattr(qdrant_client.settings, "app_env", "production")
    monkeypatch.setattr(qdrant_client.settings, "qdrant_url", "https://unresolvable.qdrant.example")
    monkeypatch.setattr(qdrant_client.settings, "qdrant_path", None)
    monkeypatch.setattr(qdrant_client, "_cloud_url_resolves", lambda url: False)
    monkeypatch.setattr(qdrant_client, "_default_local_path", lambda: "/tmp/qdrant-local")

    target = qdrant_client._resolved_target()

    assert target == {
        "mode": "cloud",
        "target": "https://unresolvable.qdrant.example",
        "fallback_from": None,
    }


def test_get_async_qdrant_client_uses_resolved_local_target(monkeypatch):
    captured: dict[str, object] = {}

    class FakeAsyncQdrantClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(
        qdrant_client,
        "_resolved_target",
        lambda: {"mode": "local", "target": "/tmp/qdrant-local", "fallback_from": "https://bad"},
    )
    monkeypatch.setattr(qdrant_client, "AsyncQdrantClient", FakeAsyncQdrantClient)

    client = qdrant_client.get_async_qdrant_client()

    assert isinstance(client, FakeAsyncQdrantClient)
    assert captured == {"path": "/tmp/qdrant-local"}


@pytest.mark.asyncio
async def test_health_report_preserves_exception_type_when_message_is_blank():
    async def ok_check():
        return {"status": "ok"}

    async def blank_error():
        raise RuntimeError("")

    with (
        patch("app.services.health.check_postgres_connection", new=ok_check),
        patch("app.services.health.check_qdrant_connection", new=blank_error),
        patch("app.services.health.check_valkey_connection", new=ok_check),
    ):
        report = await get_dependency_health_report()

    assert report["status"] == "error"
    assert report["services"]["qdrant"]["error"] == "RuntimeError('')"
    assert report["services"]["qdrant"]["error_type"] == "RuntimeError"
