import redis.asyncio as redis
from app.config import settings

_client: redis.Redis | None = None


def get_valkey() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.valkey_url, decode_responses=True)
    return _client


async def close_valkey():
    global _client
    if _client:
        await _client.aclose()
        _client = None


async def check_valkey_connection() -> dict[str, object]:
    client = get_valkey()
    pong = await client.ping()
    return {
        "status": "ok" if pong else "error",
        "url": settings.valkey_url,
    }
