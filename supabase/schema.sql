-- ===========================================
-- AIveilix Database Schema
-- Full schema for Supabase (PostgreSQL + pgvector)
-- ===========================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ===========================================
-- 1. USERS (managed by Supabase Auth)
-- ===========================================
-- Supabase Auth handles auth.users automatically
-- We create a profiles table for extra user data

CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Users can only see/edit their own profile
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ===========================================
-- 2. BUCKETS (knowledge vaults)
-- ===========================================

CREATE TABLE public.buckets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    is_private BOOLEAN DEFAULT TRUE NOT NULL,
    file_count INTEGER DEFAULT 0 NOT NULL,
    total_size_bytes BIGINT DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index for fast user lookups
CREATE INDEX idx_buckets_user_id ON public.buckets(user_id);

-- Enable RLS
ALTER TABLE public.buckets ENABLE ROW LEVEL SECURITY;

-- Users can only access their own buckets
CREATE POLICY "Users can view own buckets" ON public.buckets
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own buckets" ON public.buckets
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own buckets" ON public.buckets
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own buckets" ON public.buckets
    FOR DELETE USING (auth.uid() = user_id);

-- ===========================================
-- 3. CATEGORIES (user-defined organization)
-- ===========================================

CREATE TABLE public.categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    bucket_id UUID REFERENCES public.buckets(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#2DFFB7',
    parent_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_categories_user_id ON public.categories(user_id);
CREATE INDEX idx_categories_bucket_id ON public.categories(bucket_id);
CREATE INDEX idx_categories_parent_id ON public.categories(parent_id);

-- Enable RLS
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own categories" ON public.categories
    FOR ALL USING (auth.uid() = user_id);

-- ===========================================
-- 4. FILES (uploaded documents)
-- ===========================================

CREATE TYPE file_status AS ENUM ('pending', 'processing', 'ready', 'failed');

CREATE TABLE public.files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    bucket_id UUID NOT NULL REFERENCES public.buckets(id) ON DELETE CASCADE,
    category_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    
    -- File info
    name TEXT NOT NULL,
    original_name TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    storage_path TEXT NOT NULL,
    
    -- Processing status
    status file_status DEFAULT 'pending' NOT NULL,
    status_message TEXT,
    processed_at TIMESTAMPTZ,
    
    -- Extracted metadata
    page_count INTEGER,
    word_count INTEGER,
    language TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_files_user_id ON public.files(user_id);
CREATE INDEX idx_files_bucket_id ON public.files(bucket_id);
CREATE INDEX idx_files_category_id ON public.files(category_id);
CREATE INDEX idx_files_status ON public.files(status);

-- Enable RLS
ALTER TABLE public.files ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own files" ON public.files
    FOR ALL USING (auth.uid() = user_id);

-- ===========================================
-- 5. CHUNKS (extracted text pieces)
-- ===========================================

CREATE TABLE public.chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    bucket_id UUID NOT NULL REFERENCES public.buckets(id) ON DELETE CASCADE,
    file_id UUID NOT NULL REFERENCES public.files(id) ON DELETE CASCADE,
    
    -- Chunk content
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    
    -- Position info
    chunk_index INTEGER NOT NULL,
    page_number INTEGER,
    start_offset INTEGER,
    end_offset INTEGER,
    
    -- Vector embedding for semantic search
    embedding vector(768),
    
    -- Metadata
    token_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes for fast retrieval
CREATE INDEX idx_chunks_user_id ON public.chunks(user_id);
CREATE INDEX idx_chunks_bucket_id ON public.chunks(bucket_id);
CREATE INDEX idx_chunks_file_id ON public.chunks(file_id);
CREATE INDEX idx_chunks_content_hash ON public.chunks(content_hash);

-- Vector similarity search index (IVFFlat for performance)
CREATE INDEX idx_chunks_embedding ON public.chunks 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Full-text search index
ALTER TABLE public.chunks ADD COLUMN content_tsv tsvector 
    GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
CREATE INDEX idx_chunks_content_tsv ON public.chunks USING GIN(content_tsv);

-- Enable RLS
ALTER TABLE public.chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own chunks" ON public.chunks
    FOR ALL USING (auth.uid() = user_id);

-- ===========================================
-- 6. SUMMARIES (file/bucket summaries)
-- ===========================================

CREATE TYPE summary_type AS ENUM ('file', 'bucket', 'section');

CREATE TABLE public.summaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    bucket_id UUID REFERENCES public.buckets(id) ON DELETE CASCADE,
    file_id UUID REFERENCES public.files(id) ON DELETE CASCADE,
    
    -- Summary content
    summary_type summary_type NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    
    -- Structured data
    key_facts JSONB DEFAULT '[]'::jsonb,
    entities JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    model_used TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_summaries_user_id ON public.summaries(user_id);
CREATE INDEX idx_summaries_bucket_id ON public.summaries(bucket_id);
CREATE INDEX idx_summaries_file_id ON public.summaries(file_id);
CREATE INDEX idx_summaries_type ON public.summaries(summary_type);

-- Enable RLS
ALTER TABLE public.summaries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own summaries" ON public.summaries
    FOR ALL USING (auth.uid() = user_id);

-- ===========================================
-- 7. API_KEYS (MCP access tokens)
-- ===========================================

CREATE TABLE public.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Key info
    name TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    key_prefix TEXT NOT NULL,
    
    -- Permissions
    scopes TEXT[] DEFAULT ARRAY['read']::TEXT[],
    allowed_buckets UUID[] DEFAULT ARRAY[]::UUID[],
    
    -- Usage tracking
    last_used_at TIMESTAMPTZ,
    request_count INTEGER DEFAULT 0 NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    expires_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    revoked_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_api_keys_user_id ON public.api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON public.api_keys(key_hash);
CREATE INDEX idx_api_keys_key_prefix ON public.api_keys(key_prefix);

-- Enable RLS
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own api_keys" ON public.api_keys
    FOR ALL USING (auth.uid() = user_id);

-- ===========================================
-- 8. CONVERSATIONS (chat sessions)
-- ===========================================

CREATE TABLE public.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    bucket_id UUID REFERENCES public.buckets(id) ON DELETE SET NULL,
    
    -- Conversation info
    title TEXT,
    
    -- Settings
    mode TEXT DEFAULT 'full_scan' NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON public.conversations(user_id);
CREATE INDEX idx_conversations_bucket_id ON public.conversations(bucket_id);

-- Enable RLS
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own conversations" ON public.conversations
    FOR ALL USING (auth.uid() = user_id);

-- ===========================================
-- 9. MESSAGES (chat messages)
-- ===========================================

CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');

CREATE TABLE public.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    
    -- Message content
    role message_role NOT NULL,
    content TEXT NOT NULL,
    
    -- AI response metadata
    model_used TEXT,
    tokens_used INTEGER,
    
    -- Citations/sources used
    sources JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_messages_user_id ON public.messages(user_id);
CREATE INDEX idx_messages_conversation_id ON public.messages(conversation_id);
CREATE INDEX idx_messages_created_at ON public.messages(created_at);

-- Enable RLS
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own messages" ON public.messages
    FOR ALL USING (auth.uid() = user_id);

-- ===========================================
-- 10. ACTIONS (AI-proposed changes)
-- ===========================================

CREATE TYPE action_status AS ENUM ('pending', 'approved', 'rejected', 'executed', 'failed');
CREATE TYPE action_type AS ENUM ('categorize', 'edit_doc', 'delete', 'merge', 'split', 'tag');

CREATE TABLE public.actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES public.messages(id) ON DELETE SET NULL,
    
    -- Action details
    action_type action_type NOT NULL,
    status action_status DEFAULT 'pending' NOT NULL,
    
    -- What the AI proposes
    description TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id UUID NOT NULL,
    
    -- The change
    before_state JSONB,
    after_state JSONB,
    
    -- Execution
    executed_at TIMESTAMPTZ,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_actions_user_id ON public.actions(user_id);
CREATE INDEX idx_actions_conversation_id ON public.actions(conversation_id);
CREATE INDEX idx_actions_status ON public.actions(status);
CREATE INDEX idx_actions_target ON public.actions(target_type, target_id);

-- Enable RLS
ALTER TABLE public.actions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own actions" ON public.actions
    FOR ALL USING (auth.uid() = user_id);

-- ===========================================
-- HELPER FUNCTIONS
-- ===========================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_buckets_updated_at BEFORE UPDATE ON public.buckets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON public.categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON public.files
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_summaries_updated_at BEFORE UPDATE ON public.summaries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON public.conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_actions_updated_at BEFORE UPDATE ON public.actions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Update bucket file count and size
CREATE OR REPLACE FUNCTION update_bucket_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE public.buckets 
        SET file_count = file_count + 1,
            total_size_bytes = total_size_bytes + NEW.size_bytes
        WHERE id = NEW.bucket_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE public.buckets 
        SET file_count = file_count - 1,
            total_size_bytes = total_size_bytes - OLD.size_bytes
        WHERE id = OLD.bucket_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_bucket_stats_on_file_change
    AFTER INSERT OR DELETE ON public.files
    FOR EACH ROW EXECUTE FUNCTION update_bucket_stats();

-- ===========================================
-- SEARCH FUNCTIONS
-- ===========================================

-- Full-text search across chunks
CREATE OR REPLACE FUNCTION search_chunks(
    p_user_id UUID,
    p_bucket_id UUID,
    p_query TEXT,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    chunk_id UUID,
    file_id UUID,
    content TEXT,
    page_number INTEGER,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id AS chunk_id,
        c.file_id,
        c.content,
        c.page_number,
        ts_rank(c.content_tsv, websearch_to_tsquery('english', p_query)) AS rank
    FROM public.chunks c
    WHERE c.user_id = p_user_id
      AND c.bucket_id = p_bucket_id
      AND c.content_tsv @@ websearch_to_tsquery('english', p_query)
    ORDER BY rank DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Vector similarity search
CREATE OR REPLACE FUNCTION search_chunks_semantic(
    p_user_id UUID,
    p_bucket_id UUID,
    p_embedding vector(768),
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    chunk_id UUID,
    file_id UUID,
    content TEXT,
    page_number INTEGER,
    similarity REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id AS chunk_id,
        c.file_id,
        c.content,
        c.page_number,
        1 - (c.embedding <=> p_embedding) AS similarity
    FROM public.chunks c
    WHERE c.user_id = p_user_id
      AND c.bucket_id = p_bucket_id
      AND c.embedding IS NOT NULL
    ORDER BY c.embedding <=> p_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Full scan: get ALL chunks from a bucket
CREATE OR REPLACE FUNCTION full_scan_chunks(
    p_user_id UUID,
    p_bucket_id UUID
)
RETURNS TABLE (
    chunk_id UUID,
    file_id UUID,
    file_name TEXT,
    content TEXT,
    page_number INTEGER,
    chunk_index INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id AS chunk_id,
        c.file_id,
        f.name AS file_name,
        c.content,
        c.page_number,
        c.chunk_index
    FROM public.chunks c
    JOIN public.files f ON f.id = c.file_id
    WHERE c.user_id = p_user_id
      AND c.bucket_id = p_bucket_id
    ORDER BY f.name, c.chunk_index;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
