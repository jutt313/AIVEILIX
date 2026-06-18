from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import database


class FakeSession:
    def __init__(self):
        self.entered = False
        self.exited = False

    async def __aenter__(self):
        self.entered = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.exited = True


@pytest.mark.asyncio
async def test_db_session_closes_via_async_context_manager(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(database, "AsyncSessionLocal", lambda: session)

    async with database.db_session() as db:
        assert db is session
        assert session.entered is True
        assert session.exited is False

    assert session.exited is True


@pytest.mark.asyncio
async def test_get_db_finalizes_session_when_generator_is_closed(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(database, "AsyncSessionLocal", lambda: session)

    gen = database.get_db()
    db = await anext(gen)

    assert db is session
    assert session.entered is True
    assert session.exited is False

    await gen.aclose()

    assert session.exited is True
