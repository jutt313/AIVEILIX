from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.http_logging import install_http_logging


def _build_app() -> FastAPI:
    app = FastAPI()
    install_http_logging(app)

    @app.get("/ok")
    async def ok():
        return {"ok": True}

    @app.get("/boom")
    async def boom():
        raise RuntimeError("kaboom")

    @app.get("/forbidden")
    async def forbidden():
        raise HTTPException(status_code=403, detail="denied")

    class Payload(BaseModel):
        name: str

    @app.post("/items")
    async def create_item(payload: Payload):
        return payload.model_dump()

    return app


def test_successful_request_logs_and_sets_request_id(caplog):
    app = _build_app()

    with TestClient(app) as client, caplog.at_level(logging.INFO, logger="app.http"):
        response = client.get("/ok", headers={"origin": "http://localhost:5173"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert "[HTTP] GET /ok -> 200" in caplog.text
    assert "origin=http://localhost:5173" in caplog.text


def test_http_exception_logs_detail(caplog):
    app = _build_app()

    with TestClient(app) as client, caplog.at_level(logging.WARNING, logger="app.http"):
        response = client.get("/forbidden")

    assert response.status_code == 403
    assert "raised HTTPException status=403" in caplog.text
    assert "detail='denied'" in caplog.text
    assert "[HTTP] GET /forbidden -> 403" in caplog.text


def test_validation_error_logs_errors(caplog):
    app = _build_app()

    with TestClient(app) as client, caplog.at_level(logging.WARNING, logger="app.http"):
        response = client.post("/items", json={})

    assert response.status_code == 422
    assert "validation_failed" in caplog.text
    assert "[HTTP] POST /items -> 422" in caplog.text


def test_unhandled_exception_logs_and_returns_request_id(caplog):
    app = _build_app()

    with TestClient(app, raise_server_exceptions=False) as client, caplog.at_level(logging.ERROR, logger="app.http"):
        response = client.get("/boom")

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error."
    assert response.json()["request_id"]
    assert response.headers["X-Request-ID"] == response.json()["request_id"]
    assert "unhandled rid=" in caplog.text
    assert "[HTTP] GET /boom -> 500" in caplog.text
