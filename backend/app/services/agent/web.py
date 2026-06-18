from __future__ import annotations

import asyncio

try:
    from duckduckgo_search import DDGS
except Exception:  # pragma: no cover - optional runtime dependency
    DDGS = None

from app.services.agent.retrieval import RetrievedWebResult


# Domains that are search engines / generic landing pages — never useful as a source.
_JUNK_DOMAINS = {
    "google.com", "www.google.com", "google.co.jp", "google.co.uk",
    "bing.com", "www.bing.com",
    "duckduckgo.com", "www.duckduckgo.com",
    "search.yahoo.com", "yahoo.com", "www.yahoo.com",
    "translate.google.com", "translate.com",
    "chatgpt.com", "chat.openai.com", "openai.com",
    "open.spotify.com", "spotify.com",
    "youtube.com/results", "youtube.com",
}


def _is_junk_url(url: str) -> bool:
    from urllib.parse import urlparse
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return False
    if not host:
        return True
    if host in _JUNK_DOMAINS:
        return True
    # Bare-search pages on these engines: example bing.com/search?q=...
    for junk in ("google.", "bing.", "duckduckgo.", "yahoo."):
        if host.startswith(junk):
            return True
    return False


def _run_search(query: str, max_results: int) -> list[RetrievedWebResult]:
    if DDGS is None:
        return []
    results: list[RetrievedWebResult] = []
    with DDGS() as ddgs:
        # Pull extra to compensate for filtered-out junk
        for index, item in enumerate(ddgs.text(query, max_results=max_results * 2) or []):
            title = item.get("title") or item.get("heading") or item.get("url", "")
            url = item.get("href") or item.get("url") or ""
            snippet = item.get("body") or item.get("snippet") or ""
            if not url or _is_junk_url(url):
                continue
            results.append(
                RetrievedWebResult(
                    title=title,
                    url=url,
                    snippet=snippet,
                    score=max_results - index,
                )
            )
            if len(results) >= max_results:
                break
    return results


async def search_web(query: str, *, max_results: int = 5) -> list[RetrievedWebResult]:
    try:
        return await asyncio.to_thread(_run_search, query, max_results)
    except Exception:
        return []
