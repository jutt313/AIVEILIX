-- Migration: Add semantic search function using pgvector
-- This function performs cosine similarity search on chunk embeddings

-- Ensure pgvector extension is enabled (should already be from schema.sql)
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop ALL existing versions of this function first to avoid conflicts
DO $$
DECLARE
    func_oid oid;
BEGIN
    FOR func_oid IN 
        SELECT p.oid 
        FROM pg_proc p 
        JOIN pg_namespace n ON p.pronamespace = n.oid 
        WHERE p.proname = 'search_chunks_semantic' 
        AND n.nspname = 'public'
    LOOP
        EXECUTE 'DROP FUNCTION IF EXISTS public.search_chunks_semantic(' || 
            pg_get_function_identity_arguments(func_oid) || ')';
    END LOOP;
END $$;

-- Function to search chunks by semantic similarity
CREATE OR REPLACE FUNCTION search_chunks_semantic(
    query_embedding vector(768),
    match_user_id uuid,
    match_bucket_id uuid,
    match_count int DEFAULT 10,
    match_threshold float DEFAULT 0.5
)
RETURNS TABLE (
    id uuid,
    file_id uuid,
    content text,
    chunk_index int,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        chunks.id,
        chunks.file_id,
        chunks.content,
        chunks.chunk_index,
        1 - (chunks.embedding <=> query_embedding) AS similarity
    FROM chunks
    WHERE 
        chunks.user_id = match_user_id
        AND chunks.bucket_id = match_bucket_id
        AND chunks.embedding IS NOT NULL
        AND 1 - (chunks.embedding <=> query_embedding) > match_threshold
    ORDER BY chunks.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION search_chunks_semantic TO authenticated;
GRANT EXECUTE ON FUNCTION search_chunks_semantic TO service_role;

-- Create index on embedding column for faster similarity search (if not exists)
-- Using IVFFlat index for approximate nearest neighbor search
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'chunks_embedding_idx'
    ) THEN
        CREATE INDEX chunks_embedding_idx ON chunks 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    END IF;
END $$;

COMMENT ON FUNCTION search_chunks_semantic IS 'Semantic similarity search using pgvector cosine distance';
