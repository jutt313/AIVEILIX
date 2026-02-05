"""
Web Search Service using Google Custom Search API

Allows the AI to search the web for information not in the user's buckets.
"""
import httpx
import logging
import re
from typing import List, Dict, Optional
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Common stop words to filter out
STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just',
    'don', 'should', 'now', 'tell', 'me', 'please', 'could', 'would', 'find',
    'search', 'look', 'get', 'give', 'know', 'want', 'need', 'like', 'make'
}

# Google Custom Search API endpoint
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


def extract_search_query(message: str) -> str:
    """
    Extract a clean search query from user's message.
    Removes stop words and keeps only important keywords.

    Args:
        message: User's full message

    Returns:
        Clean search query string
    """
    # Remove punctuation except hyphens (for compound words)
    clean = re.sub(r'[^\w\s\-]', ' ', message.lower())

    # Split into words
    words = clean.split()

    # Filter out stop words and very short words
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 2]

    # Keep max 6 keywords for focused search
    keywords = keywords[:6]

    # If we got nothing, use first 5 words of original
    if not keywords:
        keywords = message.split()[:5]

    query = ' '.join(keywords)
    logger.info(f"🔍 Extracted search query: '{query}' from message: '{message[:50]}...'")

    return query


async def search_web(user_message: str, num_results: int = 5) -> List[Dict]:
    """
    Search the web using Google Custom Search API.
    Extracts keywords from user message for better results.

    Args:
        user_message: User's full message (will extract keywords)
        num_results: Number of results to return (max 10)

    Returns:
        List of search results with title, link, snippet, and domain
    """
    if not settings.google_search_api_key or not settings.google_search_cx:
        logger.warning("Google Search API not configured")
        return []

    # Extract clean search query from user message
    query = extract_search_query(user_message)

    if not query or len(query) < 3:
        logger.warning("Could not extract meaningful search query")
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
                "displayLink": item.get("displayLink", ""),
            })

        logger.info(f"✅ Web search for '{query}' returned {len(results)} results")
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
    Determine if a message needs web search for current/external information.

    Args:
        message: User's message

    Returns:
        True if web search would be helpful
    """
    message_lower = message.lower()

    # Explicit search requests
    if "search" in message_lower and ("web" in message_lower or "online" in message_lower or "internet" in message_lower or "google" in message_lower):
        return True

    # Questions about current state (who/what is NOW)
    current_state_patterns = [
        ("who is", ["now", "current", "today", "2026"]),
        ("who's", ["now", "current", "today", "2026"]),
        ("what is", ["now", "current", "today", "latest", "2026"]),
        ("what's", ["now", "current", "today", "latest", "2026"]),
    ]

    for pattern, indicators in current_state_patterns:
        if pattern in message_lower:
            # If asking "who is" + any current indicator, search
            if any(ind in message_lower for ind in indicators):
                return True
            # If asking about people/positions without docs context, search
            if any(word in message_lower for word in ["president", "minister", "ceo", "leader", "head", "director", "prime"]):
                return True

    # Time-sensitive keywords
    time_sensitive = [
        "latest", "current", "now", "today", "recent", "2026", "this year",
        "news", "weather", "stock", "price", "rate", "election"
    ]

    if any(word in message_lower for word in time_sensitive):
        return True

    # How-to queries (often need current best practices)
    if message_lower.startswith("how to") or message_lower.startswith("how do i"):
        return True

    return False
