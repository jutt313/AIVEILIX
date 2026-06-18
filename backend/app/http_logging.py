from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.http")


def _request_id(request: Request) -> str:
    rid = getattr(request.state, "request_id", None)
    if rid:
        return rid
    rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    request.state.request_id = rid
    return rid


def _request_meta(request: Request) -> dict[str, str]:
    client = request.client.host if request.client else "-"
    origin = request.headers.get("origin") or "-"
    return {"client": client, "origin": origin}


def install_http_logging(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        rid = _request_id(request)
        meta = _request_meta(request)
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "[HTTP] %s %s unhandled rid=%s origin=%s client=%s",
                request.method,
                request.url.path,
                rid,
                meta["origin"],
                meta["client"],
            )
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error.", "request_id": rid},
                headers={"X-Request-ID": rid},
            )
        response.headers.setdefault("X-Request-ID", rid)

        duration_ms = int((time.perf_counter() - started) * 1000)
        message = (
            "[HTTP] %s %s -> %s %dms rid=%s origin=%s client=%s"
            % (
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                rid,
                meta["origin"],
                meta["client"],
            )
        )
        if response.status_code >= 500:
            logger.error(message)
        elif response.status_code >= 400:
            logger.warning(message)
        else:
            logger.info(message)
        return response

    @app.exception_handler(HTTPException)
    async def log_http_exception(request: Request, exc: HTTPException):
        rid = _request_id(request)
        meta = _request_meta(request)
        logger.warning(
            "[HTTP] %s %s raised HTTPException status=%s rid=%s detail=%r origin=%s client=%s",
            request.method,
            request.url.path,
            exc.status_code,
            rid,
            exc.detail,
            meta["origin"],
            meta["client"],
        )
        response = await http_exception_handler(request, exc)
        response.headers.setdefault("X-Request-ID", rid)
        return response

    @app.exception_handler(RequestValidationError)
    async def log_validation_exception(request: Request, exc: RequestValidationError):
        rid = _request_id(request)
        meta = _request_meta(request)
        logger.warning(
            "[HTTP] %s %s validation_failed rid=%s errors=%s origin=%s client=%s",
            request.method,
            request.url.path,
            rid,
            exc.errors(),
            meta["origin"],
            meta["client"],
        )
        response = await request_validation_exception_handler(request, exc)
        response.headers.setdefault("X-Request-ID", rid)
        return response
