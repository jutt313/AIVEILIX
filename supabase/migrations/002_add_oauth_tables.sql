-- OAuth2 Tables for MCP Authentication
-- Migration: 002_add_oauth_tables.sql

-- OAuth Clients Table
-- Stores registered OAuth applications (like ChatGPT connector)
CREATE TABLE IF NOT EXISTS oauth_clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(64) UNIQUE NOT NULL,
    client_secret_hash VARCHAR(128) NOT NULL,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    redirect_uri TEXT NOT NULL,
    scopes TEXT[] DEFAULT ARRAY['read:buckets', 'read:files', 'query', 'chat'],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Index for fast client_id lookups
CREATE INDEX IF NOT EXISTS idx_oauth_clients_client_id ON oauth_clients(client_id);
CREATE INDEX IF NOT EXISTS idx_oauth_clients_user_id ON oauth_clients(user_id);

-- OAuth Authorization Codes Table
-- Temporary codes exchanged for tokens (short-lived, ~10 minutes)
CREATE TABLE IF NOT EXISTS oauth_authorization_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_hash VARCHAR(128) UNIQUE NOT NULL,
    client_id VARCHAR(64) NOT NULL REFERENCES oauth_clients(client_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    redirect_uri TEXT NOT NULL,
    scope TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Index for code lookup and cleanup
CREATE INDEX IF NOT EXISTS idx_oauth_auth_codes_code_hash ON oauth_authorization_codes(code_hash);
CREATE INDEX IF NOT EXISTS idx_oauth_auth_codes_expires_at ON oauth_authorization_codes(expires_at);

-- OAuth Tokens Table
-- Access and refresh tokens
CREATE TABLE IF NOT EXISTS oauth_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    access_token_hash VARCHAR(128) UNIQUE NOT NULL,
    refresh_token_hash VARCHAR(128) UNIQUE,
    client_id VARCHAR(64) NOT NULL REFERENCES oauth_clients(client_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    scope TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    refresh_expires_at TIMESTAMP WITH TIME ZONE,
    is_revoked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Indexes for token operations
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_access_hash ON oauth_tokens(access_token_hash);
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_refresh_hash ON oauth_tokens(refresh_token_hash);
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_user_id ON oauth_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_oauth_tokens_expires_at ON oauth_tokens(expires_at);

-- Enable Row Level Security
ALTER TABLE oauth_clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE oauth_authorization_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE oauth_tokens ENABLE ROW LEVEL SECURITY;

-- RLS Policies for oauth_clients
-- Users can only see/manage their own clients
CREATE POLICY "Users can view own OAuth clients"
    ON oauth_clients FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own OAuth clients"
    ON oauth_clients FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own OAuth clients"
    ON oauth_clients FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own OAuth clients"
    ON oauth_clients FOR DELETE
    USING (auth.uid() = user_id);

-- RLS Policies for oauth_authorization_codes
CREATE POLICY "Users can view own auth codes"
    ON oauth_authorization_codes FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create auth codes"
    ON oauth_authorization_codes FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "System can update auth codes"
    ON oauth_authorization_codes FOR UPDATE
    USING (true);

-- RLS Policies for oauth_tokens
CREATE POLICY "Users can view own tokens"
    ON oauth_tokens FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can insert tokens"
    ON oauth_tokens FOR INSERT
    WITH CHECK (true);

CREATE POLICY "System can update tokens"
    ON oauth_tokens FOR UPDATE
    USING (true);

CREATE POLICY "Users can revoke own tokens"
    ON oauth_tokens FOR DELETE
    USING (auth.uid() = user_id);

-- Function to clean up expired authorization codes
CREATE OR REPLACE FUNCTION cleanup_expired_oauth_codes()
RETURNS void AS $$
BEGIN
    DELETE FROM oauth_authorization_codes
    WHERE expires_at < now() OR used = true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean up expired/revoked tokens
CREATE OR REPLACE FUNCTION cleanup_expired_oauth_tokens()
RETURNS void AS $$
BEGIN
    DELETE FROM oauth_tokens
    WHERE expires_at < now() OR is_revoked = true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Updated_at trigger for oauth_clients
CREATE OR REPLACE FUNCTION update_oauth_clients_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_oauth_clients_updated_at
    BEFORE UPDATE ON oauth_clients
    FOR EACH ROW
    EXECUTE FUNCTION update_oauth_clients_updated_at();

-- Comments for documentation
COMMENT ON TABLE oauth_clients IS 'Registered OAuth2 client applications';
COMMENT ON TABLE oauth_authorization_codes IS 'Temporary authorization codes for OAuth2 flow';
COMMENT ON TABLE oauth_tokens IS 'OAuth2 access and refresh tokens';
COMMENT ON COLUMN oauth_clients.client_id IS 'Public client identifier';
COMMENT ON COLUMN oauth_clients.client_secret_hash IS 'SHA-256 hash of client secret';
COMMENT ON COLUMN oauth_tokens.access_token_hash IS 'SHA-256 hash of access token';
COMMENT ON COLUMN oauth_tokens.refresh_token_hash IS 'SHA-256 hash of refresh token';
