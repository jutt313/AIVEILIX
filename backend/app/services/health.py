from __future__ import annotations

from app.database import check_postgres_connection
from app.qdrant_client import check_qdrant_connection
from app.valkey import check_valkey_connection


async def get_dependency_health_report() -> dict[str, object]:
    services: dict[str, dict[str, object]] = {}

    for name, check in (
        ("postgres", check_postgres_connection),
        ("qdrant", check_qdrant_connection),
        ("valkey", check_valkey_connection),
    ):
        try:
            services[name] = await check()
        except Exception as exc:
            message = str(exc).strip() or repr(exc) or type(exc).__name__
            services[name] = {
                "status": "error",
                "error": message,
                "error_type": type(exc).__name__,
            }

    overall = "ok" if all(service["status"] == "ok" for service in services.values()) else "error"
    return {
        "status": overall,
        "services": services,
    }
