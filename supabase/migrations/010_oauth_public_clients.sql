-- Migration: Allow public OAuth client registration (DCR)
-- ChatGPT/Claude register clients before any user is authenticated.
-- user_id is set during the authorization flow when user logs in.

-- Make user_id nullable on oauth_clients for public DCR
ALTER TABLE oauth_clients ALTER COLUMN user_id DROP NOT NULL;

-- Drop the existing foreign key constraint and re-add as nullable
-- (the FK itself allows NULL values, we just needed to drop NOT NULL)

-- Update RLS policies to allow service role to insert clients without user_id
-- The service role key bypasses RLS, so no policy changes needed.

-- Add comment
COMMENT ON COLUMN oauth_clients.user_id IS 'Owner user ID. NULL for clients registered via DCR before user authorization.';
