-- Migration: Switch embeddings from OpenAI (3072 dims) to Voyage AI (1024 dims)
-- Run this in Supabase SQL Editor

-- Step 1: Drop old IVFFlat index (built for 3072 dims)
DROP INDEX IF EXISTS chunks_embedding_idx;

-- Step 2: Clear existing embeddings (incompatible dimensions)
UPDATE chunks SET embedding = NULL;

-- Step 3: Change column from vector(3072) to vector(1024)
ALTER TABLE chunks
  ALTER COLUMN embedding TYPE vector(1024)
  USING NULL;

-- Step 4: Recreate IVFFlat index for 1024 dims
CREATE INDEX chunks_embedding_idx
  ON chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Step 5: Update search_chunks_semantic function for 1024 dims
CREATE OR REPLACE FUNCTION search_chunks_semantic(
  query_embedding vector(1024),
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
    1 - (c.embedding <=> query_embedding) AS similarity
  FROM chunks c
  WHERE
    c.user_id = match_user_id
    AND c.bucket_id = match_bucket_id
    AND c.embedding IS NOT NULL
    AND 1 - (c.embedding <=> query_embedding) > match_threshold
  ORDER BY c.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Step 6: Update match_chunks function for 1024 dims
CREATE OR REPLACE FUNCTION match_chunks(
  query_embedding vector(1024),
  match_bucket_id uuid,
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10
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
    1 - (c.embedding <=> query_embedding) AS similarity
  FROM chunks c
  WHERE
    c.bucket_id = match_bucket_id
    AND c.embedding IS NOT NULL
    AND 1 - (c.embedding <=> query_embedding) > match_threshold
  ORDER BY c.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
