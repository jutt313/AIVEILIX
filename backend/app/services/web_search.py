"""
Web Search Service using Google Custom Search API

Allows the AI to search the web for information not in the user's buckets.
"""
import httpx
import logging
from typing import List, Dict, Optional
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Google Custom Search API endpoint
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


async def search_web(query: str, num_results: int = 5) -> List[Dict]:
    """
    Search the web using Google Custom Search API.
    
    Args:
        query: Search query string
        num_results: Number of results to return (max 10)
    
    Returns:
        List of search results with title, link, and snippet
    """
    if not settings.google_search_api_key or not settings.google_search_cx:
        logger.warning("Google Search API not configured")
        return []
    
    try:
        params = {
            "key": settings.google_search_api_key,
            "cx": settings.google_search_cx,
            "q": query,
            "num": min(num_results, 10),  # API max is 10
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(GOOGLE_SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()
        
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            })
        
        logger.info(f"Web search for '{query}' returned {len(results)} results")
        return results
    
    except httpx.HTTPStatusError as e:
        logger.error(f"Google Search API HTTP error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return []


def format_search_results_for_context(results: List[Dict]) -> str:
    """
    Format search results as context for the AI.
    
    Args:
        results: List of search results
    
    Returns:
        Formatted string for injection into AI context
    """
    if not results:
        return ""
    
    formatted = "[Web Search Results]\n\n"
    for i, result in enumerate(results, 1):
        formatted += f"{i}. **{result['title']}**\n"
        formatted += f"   URL: {result['link']}\n"
        formatted += f"   {result['snippet']}\n\n"
    
    return formatted


def should_search_web(message: str) -> bool:
    """
    Heuristic to determine if a message likely needs web search.
    
    Args:
        message: User's message
    
    Returns:
        True if web search would be helpful
    """
    # Keywords that suggest needing current/external info
    web_search_triggers = [
        "search the web",
        "search online",
        "look up",
        "find online",
        "what is the latest",
        "current",
        "today",
        "recent news",
        "2024",
        "2025",
        "2026",
        "who is",
        "what is",
        "how to",
        "where can i",
        "price of",
        "weather",
        "stock",
        "news about",
    ]
    
    message_lower = message.lower()
    
    # Explicit request to search web
    if "search" in message_lower and ("web" in message_lower or "online" in message_lower or "internet" in message_lower):
        return True
    
    # Check for trigger phrases
    for trigger in web_search_triggers:
        if trigger in message_lower:
            return True
    
    return False
