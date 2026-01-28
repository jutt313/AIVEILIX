-- Migration: Upgrade to OpenAI text-embedding-3-large (3072 dimensions)
-- Full end-to-end migration: enable extension, drop old indexes, alter column,
-- drop old search functions, recreate search function, and create HNSW index using halfvec.

-- Ensure pgvector extension is enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 1: Drop ALL indexes on the embedding column (whatever name they have)
DO $$
DECLARE
    idx_name text;
BEGIN
    FOR idx_name IN
        SELECT i.relname
        FROM pg_index x
        JOIN pg_class i ON i.oid = x.indexrelid
        JOIN pg_class t ON t.oid = x.indrelid
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(x.indkey)
        WHERE t.relname = 'chunks' AND a.attname = 'embedding'
    LOOP
        EXECUTE 'DROP INDEX IF EXISTS ' || quote_ident(idx_name);
    END LOOP;
END $$;

-- Also drop known names just in case
DROP INDEX IF EXISTS chunks_embedding_idx;
DROP INDEX IF EXISTS chunks_embedding_3072_idx;
DROP INDEX IF EXISTS chunks_embedding_hnsw_idx;

-- Step 2: Alter the embedding column to 3072 dimensions
-- This will clear existing embeddings (they need to be regenerated with OpenAI anyway)
ALTER TABLE chunks 
ALTER COLUMN embedding TYPE vector(3072)
USING NULL;

-- Step 3: Drop ALL existing versions of the search function
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

-- Step 4: Create new function for 3072-dimension embeddings
-- Uses halfvec cast to match the HNSW index for optimal performance
CREATE OR REPLACE FUNCTION search_chunks_semantic(
    query_embedding vector(3072),
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
        c.id,
        c.file_id,
        c.content,
        c.chunk_index,
        (1 - (c.embedding::halfvec(3072) <=> query_embedding::halfvec(3072)))::float AS similarity
    FROM chunks c
    WHERE 
        c.user_id = match_user_id
        AND c.bucket_id = match_bucket_id
        AND c.embedding IS NOT NULL
        AND (1 - (c.embedding::halfvec(3072) <=> query_embedding::halfvec(3072))) > match_threshold
    ORDER BY c.embedding::halfvec(3072) <=> query_embedding::halfvec(3072)
    LIMIT match_count;
END;
$$;

-- Step 5: Grant permissions
GRANT EXECUTE ON FUNCTION search_chunks_semantic TO authenticated;
GRANT EXECUTE ON FUNCTION search_chunks_semantic TO service_role;

-- Step 6: Create HNSW index using halfvec cast (supports 3072 dimensions)
-- Use cosine operator class to match '<=>' operator used above.
-- NOTE: Requires pgvector >= 0.7.0 (halfvec support).
CREATE INDEX chunks_embedding_hnsw_idx
ON chunks
USING hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops)
WITH (m = 16, ef_construction = 64);

COMMENT ON FUNCTION search_chunks_semantic IS 'Semantic similarity search using OpenAI text-embedding-3-large (3072 dims) with pgvector HNSW index (halfvec cast)';
