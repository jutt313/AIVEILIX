from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.http_logging import install_http_logging
from app.logging_config import setup_logging

setup_logging(level="DEBUG" if settings.app_env == "development" else "INFO")
from app.database import engine
from app.qdrant_client import close_qdrant_clients
from app.services.health import get_dependency_health_report
from app.services.qdrant.file_indexer import ensure_collections
from app.valkey import close_valkey
from app.api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    health_report = await get_dependency_health_report()
    if health_report["status"] != "ok":
        raise RuntimeError(f"Dependency startup checks failed: {health_report}")

    app.state.startup_health = health_report

    # Ensure Qdrant collections exist with correct vector config
    await ensure_collections()

    yield
    # Shutdown
    await close_qdrant_clients()
    await close_valkey()
    await engine.dispose()


app = FastAPI(
    title="AIveilix API",
    version="1.0.0",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_http_logging(app)

app.include_router(v1_router, prefix="/v1")


@app.get("/health")
async def health():
    report = await get_dependency_health_report()
    status_code = 200 if report["status"] == "ok" else 503
    return JSONResponse(status_code=status_code, content=report)
