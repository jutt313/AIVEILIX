"""
Semantic Search Service using pgvector

Provides vector similarity search across document chunks.
"""
import logging
from typing import List, Dict, Optional
from app.config import get_settings
from app.services.supabase import get_supabase
from app.services.file_processor import generate_query_embedding

settings = get_settings()
logger = logging.getLogger(__name__)


async def semantic_search(
    query: str,
    user_id: str,
    bucket_id: str,
    limit: int = 10,
    similarity_threshold: float = 0.5
) -> List[Dict]:
    """
    Search for semantically similar chunks using vector similarity.
    
    Args:
        query: Search query text
        user_id: User ID for filtering
        bucket_id: Bucket ID to search in
        limit: Maximum number of results
        similarity_threshold: Minimum similarity score (0-1)
    
    Returns:
        List of matching chunks with similarity scores
    """
    # Generate query embedding
    query_embedding = generate_query_embedding(query)
    
    if not query_embedding:
        logger.warning("Could not generate query embedding - falling back to keyword search")
        return []
    
    try:
        supabase = get_supabase()
        
        # Use pgvector cosine similarity search via RPC
        # The function search_chunks_semantic should be defined in your Supabase schema
        result = supabase.rpc(
            "search_chunks_semantic",
            {
                "query_embedding": query_embedding,
                "match_user_id": user_id,
                "match_bucket_id": bucket_id,
                "match_count": limit,
                "match_threshold": similarity_threshold
            }
        ).execute()
        
        if not result.data:
            return []
        
        # Format results
        formatted_results = []
        for row in result.data:
            formatted_results.append({
                "chunk_id": row.get("id"),
                "file_id": row.get("file_id"),
                "content": row.get("content"),
                "similarity": row.get("similarity"),
                "chunk_index": row.get("chunk_index"),
            })
        
        logger.info(f"Semantic search for '{query[:50]}...' returned {len(formatted_results)} results")
        return formatted_results
    
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return []


async def hybrid_search(
    query: str,
    user_id: str,
    bucket_id: str,
    limit: int = 10
) -> List[Dict]:
    """
    Hybrid search combining semantic and keyword search.
    
    Args:
        query: Search query text
        user_id: User ID for filtering
        bucket_id: Bucket ID to search in
        limit: Maximum number of results
    
    Returns:
        Combined and deduplicated results from both search types
    """
    results = []
    seen_chunk_ids = set()
    
    # Try semantic search first
    semantic_results = await semantic_search(query, user_id, bucket_id, limit=limit)
    
    for result in semantic_results:
        chunk_id = result.get("chunk_id")
        if chunk_id and chunk_id not in seen_chunk_ids:
            result["match_type"] = "semantic"
            results.append(result)
            seen_chunk_ids.add(chunk_id)
    
    # If we don't have enough results, supplement with keyword search
    if len(results) < limit:
        try:
            supabase = get_supabase()
            
            # Simple keyword search using ilike
            keyword_results = supabase.table("chunks").select(
                "id, file_id, content, chunk_index"
            ).eq("bucket_id", bucket_id).eq("user_id", user_id).ilike(
                "content", f"%{query}%"
            ).limit(limit - len(results)).execute()
            
            for row in keyword_results.data or []:
                chunk_id = row.get("id")
                if chunk_id and chunk_id not in seen_chunk_ids:
                    results.append({
                        "chunk_id": chunk_id,
                        "file_id": row.get("file_id"),
                        "content": row.get("content"),
                        "similarity": None,
                        "chunk_index": row.get("chunk_index"),
                        "match_type": "keyword"
                    })
                    seen_chunk_ids.add(chunk_id)
        except Exception as e:
            logger.error(f"Keyword search fallback error: {e}")
    
    return results[:limit]


def format_semantic_results_for_context(results: List[Dict], file_names: Dict[str, str]) -> str:
    """
    Format semantic search results for inclusion in AI context.
    
    Args:
        results: List of search results
        file_names: Mapping of file_id to file name
    
    Returns:
        Formatted string for AI context
    """
    if not results:
        return ""
    
    formatted = "[Relevant Document Excerpts]\n\n"
    
    for i, result in enumerate(results, 1):
        file_id = result.get("file_id", "")
        file_name = file_names.get(file_id, "Unknown")
        content = result.get("content", "")[:500]  # Truncate long content
        similarity = result.get("similarity")
        match_type = result.get("match_type", "unknown")
        
        formatted += f"{i}. **{file_name}**"
        if similarity:
            formatted += f" (relevance: {similarity:.2f})"
        formatted += f"\n{content}\n\n"
    
    return formatted
