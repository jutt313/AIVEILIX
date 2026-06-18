BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

CREATE TYPE auth_provider AS ENUM ('email', 'google', 'github');
CREATE TYPE theme_mode AS ENUM ('light', 'dark');
CREATE TYPE llm_provider AS ENUM ('claude', 'gemini', 'gpt4o', 'kimi');
CREATE TYPE subscription_plan AS ENUM ('free', 'individual', 'team', 'business');
CREATE TYPE subscription_status AS ENUM ('active', 'cancelled', 'past_due');
CREATE TYPE file_status AS ENUM ('uploading', 'processing', 'ready', 'failed');
CREATE TYPE embedding_status AS ENUM ('pending', 'embedded', 'failed');
CREATE TYPE message_role AS ENUM ('user', 'assistant');
CREATE TYPE api_key_type AS ENUM ('bucket', 'account');
CREATE TYPE team_role AS ENUM ('viewer', 'editor', 'admin');
CREATE TYPE team_member_status AS ENUM ('pending', 'accepted', 'rejected');
CREATE TYPE team_bucket_permission AS ENUM ('read', 'write', 'admin');
CREATE TYPE notification_type AS ENUM ('info', 'success', 'warning', 'error');
CREATE TYPE event_status AS ENUM ('started', 'completed', 'failed');
CREATE TYPE web_search_mode AS ENUM ('smart', 'bucket_only', 'always_search');
CREATE TYPE follow_up_mode AS ENUM ('all_at_once', 'one_by_one');

CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION enforce_conversation_limit()
RETURNS TRIGGER AS $$
DECLARE
    conversation_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO conversation_count
    FROM conversations
    WHERE bucket_id = NEW.bucket_id;

    IF conversation_count >= 50 THEN
        RAISE EXCEPTION 'Bucket % already has the maximum of 50 conversation threads', NEW.bucket_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email CITEXT NOT NULL UNIQUE,
    password_hash TEXT,
    provider auth_provider NOT NULL,
    provider_id TEXT,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    two_factor_secret TEXT,
    two_factor_backup_codes JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    theme theme_mode NOT NULL DEFAULT 'dark',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    timezone VARCHAR(100) NOT NULL DEFAULT 'UTC',
    preferred_llm llm_provider NOT NULL DEFAULT 'claude',
    follow_up_mode follow_up_mode NOT NULL DEFAULT 'all_at_once',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE buckets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    mcp_url TEXT UNIQUE,
    mcp_token TEXT UNIQUE,
    account_mcp_url TEXT,
    account_mcp_token TEXT,
    color VARCHAR(7) NOT NULL DEFAULT '#3B82F6',
    icon VARCHAR(50) NOT NULL DEFAULT 'folder',
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    storage_used BIGINT NOT NULL DEFAULT 0 CHECK (storage_used >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT buckets_name_per_user_unique UNIQUE (user_id, name)
);

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket_id UUID NOT NULL REFERENCES buckets(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    color VARCHAR(7) NOT NULL DEFAULT '#3B82F6',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT categories_name_per_bucket_unique UNIQUE (bucket_id, name)
);

CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bucket_id UUID NOT NULL REFERENCES buckets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    size BIGINT NOT NULL CHECK (size >= 0),
    r2_path TEXT NOT NULL,
    layout_json_path TEXT,
    status file_status NOT NULL DEFAULT 'uploading',
    page_count INTEGER NOT NULL DEFAULT 0 CHECK (page_count >= 0),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE file_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL CHECK (version_number >= 1),
    r2_path TEXT NOT NULL,
    size BIGINT NOT NULL CHECK (size >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT file_versions_file_version_unique UNIQUE (file_id, version_number)
);

CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    bucket_id UUID NOT NULL REFERENCES buckets(id) ON DELETE CASCADE,
    page INTEGER NOT NULL CHECK (page >= 1),
    content TEXT NOT NULL,
    block_id VARCHAR(255) NOT NULL,
    nearby_image_id VARCHAR(255),
    token_count INTEGER NOT NULL DEFAULT 0 CHECK (token_count >= 0),
    status embedding_status NOT NULL DEFAULT 'pending',
    retry_count INTEGER NOT NULL DEFAULT 0 CHECK (retry_count >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES files(id) ON DELETE CASCADE,
    bucket_id UUID REFERENCES buckets(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT summaries_exactly_one_target CHECK (num_nonnulls(file_id, bucket_id) = 1)
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bucket_id UUID NOT NULL REFERENCES buckets(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    web_search_mode web_search_mode NOT NULL DEFAULT 'smart',
    follow_up_mode follow_up_mode NOT NULL DEFAULT 'all_at_once',
    file_scope_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    parent_message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    chunks_used JSONB NOT NULL DEFAULT '[]'::jsonb,
    token_count INTEGER NOT NULL DEFAULT 0 CHECK (token_count >= 0),
    embedding_status embedding_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversation_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    bucket_id UUID NOT NULL REFERENCES buckets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    token_count INTEGER NOT NULL DEFAULT 0 CHECK (token_count >= 0),
    status embedding_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT conversation_chunks_message_chunk_unique UNIQUE (message_id, chunk_index)
);

CREATE TABLE oauth_authorization_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code TEXT NOT NULL UNIQUE,
    code_challenge TEXT NOT NULL,
    redirect_uri TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE oauth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL UNIQUE,
    refresh_token TEXT NOT NULL UNIQUE,
    provider auth_provider NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bucket_id UUID REFERENCES buckets(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    type api_key_type NOT NULL,
    name VARCHAR(255) NOT NULL,
    last_used_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT api_keys_bucket_scope_valid CHECK (
        (type = 'bucket' AND bucket_id IS NOT NULL) OR
        (type = 'account' AND bucket_id IS NULL)
    )
);

CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    member_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role team_role NOT NULL DEFAULT 'viewer',
    status team_member_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT team_members_unique_pair UNIQUE (owner_user_id, member_user_id),
    CONSTRAINT team_members_distinct_users CHECK (owner_user_id <> member_user_id)
);

CREATE TABLE team_bucket_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_member_id UUID NOT NULL REFERENCES team_members(id) ON DELETE CASCADE,
    bucket_id UUID NOT NULL REFERENCES buckets(id) ON DELETE CASCADE,
    permission team_bucket_permission NOT NULL DEFAULT 'read',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT team_bucket_access_unique UNIQUE (team_member_id, bucket_id)
);

CREATE TABLE team_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_member_id UUID NOT NULL REFERENCES team_members(id) ON DELETE CASCADE,
    bucket_id UUID NOT NULL REFERENCES buckets(id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    plan subscription_plan NOT NULL DEFAULT 'free',
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    status subscription_status NOT NULL DEFAULT 'active',
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bucket_id UUID REFERENCES buckets(id) ON DELETE SET NULL,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
    endpoint VARCHAR(255) NOT NULL,
    tokens_used INTEGER NOT NULL DEFAULT 0 CHECK (tokens_used >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    month DATE NOT NULL,
    storage_used BIGINT NOT NULL DEFAULT 0 CHECK (storage_used >= 0),
    chat_messages_count INTEGER NOT NULL DEFAULT 0 CHECK (chat_messages_count >= 0),
    mcp_calls_count INTEGER NOT NULL DEFAULT 0 CHECK (mcp_calls_count >= 0),
    buckets_count INTEGER NOT NULL DEFAULT 0 CHECK (buckets_count >= 0),
    files_count INTEGER NOT NULL DEFAULT 0 CHECK (files_count >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT usage_tracking_user_month_unique UNIQUE (user_id, month)
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE investigation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    event VARCHAR(255) NOT NULL,
    status event_status NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE error_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    file_id UUID REFERENCES files(id) ON DELETE SET NULL,
    service VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX summaries_file_unique_idx
    ON summaries (file_id)
    WHERE file_id IS NOT NULL;

CREATE UNIQUE INDEX summaries_bucket_unique_idx
    ON summaries (bucket_id)
    WHERE bucket_id IS NOT NULL;

CREATE INDEX buckets_user_id_idx ON buckets (user_id);
CREATE INDEX categories_bucket_id_idx ON categories (bucket_id);
CREATE INDEX files_bucket_id_idx ON files (bucket_id);
CREATE INDEX files_user_id_idx ON files (user_id);
CREATE INDEX files_category_id_idx ON files (category_id);
CREATE INDEX files_status_idx ON files (status);
CREATE INDEX file_versions_file_id_idx ON file_versions (file_id);
CREATE INDEX chunks_file_id_idx ON chunks (file_id);
CREATE INDEX chunks_bucket_id_idx ON chunks (bucket_id);
CREATE INDEX chunks_status_idx ON chunks (status);
CREATE INDEX conversations_bucket_updated_idx ON conversations (bucket_id, updated_at DESC);
CREATE INDEX conversations_user_id_idx ON conversations (user_id);
CREATE INDEX messages_conversation_created_idx ON messages (conversation_id, created_at ASC);
CREATE INDEX messages_parent_message_id_idx ON messages (parent_message_id);
CREATE INDEX messages_embedding_status_idx ON messages (embedding_status);
CREATE INDEX conversation_chunks_conversation_idx ON conversation_chunks (conversation_id, created_at ASC);
CREATE INDEX conversation_chunks_bucket_idx ON conversation_chunks (bucket_id);
CREATE INDEX conversation_chunks_user_idx ON conversation_chunks (user_id);
CREATE INDEX conversation_chunks_status_idx ON conversation_chunks (status);
CREATE INDEX oauth_authorization_codes_user_id_idx ON oauth_authorization_codes (user_id);
CREATE INDEX oauth_authorization_codes_expires_at_idx ON oauth_authorization_codes (expires_at);
CREATE INDEX oauth_tokens_user_id_idx ON oauth_tokens (user_id);
CREATE INDEX oauth_tokens_provider_idx ON oauth_tokens (provider);
CREATE INDEX api_keys_user_id_idx ON api_keys (user_id);
CREATE INDEX api_keys_bucket_id_idx ON api_keys (bucket_id);
CREATE INDEX team_members_owner_idx ON team_members (owner_user_id);
CREATE INDEX team_members_member_idx ON team_members (member_user_id);
CREATE INDEX team_bucket_access_bucket_idx ON team_bucket_access (bucket_id);
CREATE INDEX team_activity_log_bucket_created_idx ON team_activity_log (bucket_id, created_at DESC);
CREATE INDEX api_usage_user_created_idx ON api_usage (user_id, created_at DESC);
CREATE INDEX api_usage_bucket_idx ON api_usage (bucket_id);
CREATE INDEX notifications_user_read_created_idx ON notifications (user_id, is_read, created_at DESC);
CREATE INDEX investigation_events_file_created_idx ON investigation_events (file_id, created_at ASC);
CREATE INDEX error_logs_user_idx ON error_logs (user_id);
CREATE INDEX error_logs_file_idx ON error_logs (file_id);
CREATE INDEX error_logs_resolved_idx ON error_logs (resolved);

CREATE TRIGGER users_set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER profiles_set_updated_at
BEFORE UPDATE ON profiles
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER buckets_set_updated_at
BEFORE UPDATE ON buckets
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER files_set_updated_at
BEFORE UPDATE ON files
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER conversations_set_updated_at
BEFORE UPDATE ON conversations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER usage_tracking_set_updated_at
BEFORE UPDATE ON usage_tracking
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER conversations_max_20_per_bucket
BEFORE INSERT ON conversations
FOR EACH ROW
EXECUTE FUNCTION enforce_conversation_limit();

INSERT INTO schema_migrations (version)
VALUES ('2026-04-01_initial_schema');

COMMIT;
