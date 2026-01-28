-- OAuth2 PKCE Support and Error Logging
-- Migration: 003_add_pkce_support.sql
-- NOTE: This migration requires migration 002_add_oauth_tables.sql to be run first

-- Check if oauth_authorization_codes table exists before altering
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'oauth_authorization_codes') THEN
        -- Add PKCE columns to oauth_authorization_codes table
        ALTER TABLE oauth_authorization_codes
        ADD COLUMN IF NOT EXISTS code_challenge VARCHAR(128),
        ADD COLUMN IF NOT EXISTS code_challenge_method VARCHAR(10) DEFAULT 'S256';

        -- Add resource parameter support (RFC 8707 Resource Indicators)
        ALTER TABLE oauth_authorization_codes
        ADD COLUMN IF NOT EXISTS resource TEXT;
    ELSE
        RAISE NOTICE 'Table oauth_authorization_codes does not exist. Please run migration 002_add_oauth_tables.sql first.';
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'oauth_tokens') THEN
        ALTER TABLE oauth_tokens
        ADD COLUMN IF NOT EXISTS resource TEXT,
        ADD COLUMN IF NOT EXISTS audience TEXT;
    ELSE
        RAISE NOTICE 'Table oauth_tokens does not exist. Please run migration 002_add_oauth_tables.sql first.';
    END IF;
END $$;

-- Add indexes for PKCE lookups (only if tables exist)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'oauth_authorization_codes') THEN
        CREATE INDEX IF NOT EXISTS idx_oauth_auth_codes_code_challenge ON oauth_authorization_codes(code_challenge);
        
        -- Comments for documentation
        COMMENT ON COLUMN oauth_authorization_codes.code_challenge IS 'PKCE code challenge (base64url(SHA256(code_verifier)))';
        COMMENT ON COLUMN oauth_authorization_codes.code_challenge_method IS 'PKCE method: S256 or plain';
        COMMENT ON COLUMN oauth_authorization_codes.resource IS 'RFC 8707 Resource Indicator';
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'oauth_tokens') THEN
        CREATE INDEX IF NOT EXISTS idx_oauth_tokens_resource ON oauth_tokens(resource);
        CREATE INDEX IF NOT EXISTS idx_oauth_tokens_audience ON oauth_tokens(audience);
        
        -- Comments for documentation
        COMMENT ON COLUMN oauth_tokens.resource IS 'RFC 8707 Resource Indicator echoed from authorization';
        COMMENT ON COLUMN oauth_tokens.audience IS 'Token audience (MCP server URL)';
    END IF;
END $$;

-- Error Logs Table
-- Stores detailed error information for debugging and monitoring
CREATE TABLE IF NOT EXISTS error_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    request_body JSONB,
    headers JSONB,
    ip_address INET,
    correlation_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    request_duration_ms NUMERIC,
    is_timeout BOOLEAN DEFAULT false,
    query_params JSONB,
    query_details JSONB,
    additional_context JSONB
);

-- Indexes for error logs
CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_error_logs_user_id ON error_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_endpoint ON error_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_error_logs_error_type ON error_logs(error_type);
CREATE INDEX IF NOT EXISTS idx_error_logs_correlation_id ON error_logs(correlation_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_is_timeout ON error_logs(is_timeout);
CREATE INDEX IF NOT EXISTS idx_error_logs_duration ON error_logs(request_duration_ms) WHERE request_duration_ms IS NOT NULL;

-- Enable Row Level Security for error_logs
ALTER TABLE error_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for error_logs
-- Users can only view their own errors, admins can view all
CREATE POLICY "Users can view own error logs"
    ON error_logs FOR SELECT
    USING (auth.uid() = user_id OR auth.jwt() ->> 'role' = 'admin');

-- System can insert error logs (for logging from backend)
CREATE POLICY "System can insert error logs"
    ON error_logs FOR INSERT
    WITH CHECK (true);

-- Comments for documentation
COMMENT ON TABLE error_logs IS 'Application error logs for debugging and monitoring';
COMMENT ON COLUMN error_logs.correlation_id IS 'Request correlation ID for tracing';
COMMENT ON COLUMN error_logs.request_body IS 'Sanitized request body (sensitive data removed)';
COMMENT ON COLUMN error_logs.headers IS 'Sanitized request headers (sensitive data removed)';
