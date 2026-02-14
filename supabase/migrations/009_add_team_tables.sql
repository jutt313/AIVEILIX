-- Migration: Add Team Collaboration Tables
-- Description: team_members, team_bucket_access, team_activity_log + modify profiles, files, messages

-- ============================================================
-- 0. Helper Function (create if not exists)
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 1. New Tables
-- ============================================================

-- Team Members (invited by an owner)
CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    member_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,  -- the auth account created for this member
    name TEXT NOT NULL,
    real_email TEXT NOT NULL,
    aiveilix_email TEXT NOT NULL UNIQUE,  -- name@aiveilix.com
    color TEXT NOT NULL DEFAULT '#2DFFB7',  -- hex color for tracking
    show_name BOOLEAN NOT NULL DEFAULT true,  -- admin toggle: show name on hover
    is_active BOOLEAN NOT NULL DEFAULT true,
    removed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Team Bucket Access (per-member per-bucket permissions)
CREATE TABLE IF NOT EXISTS team_bucket_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_member_id UUID NOT NULL REFERENCES team_members(id) ON DELETE CASCADE,
    bucket_id UUID NOT NULL REFERENCES buckets(id) ON DELETE CASCADE,
    can_view BOOLEAN NOT NULL DEFAULT true,
    can_chat BOOLEAN NOT NULL DEFAULT false,
    can_upload BOOLEAN NOT NULL DEFAULT false,
    can_delete BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(team_member_id, bucket_id)
);

-- Team Activity Log
CREATE TABLE IF NOT EXISTS team_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    member_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    team_member_id UUID REFERENCES team_members(id) ON DELETE SET NULL,
    bucket_id UUID REFERENCES buckets(id) ON DELETE SET NULL,
    action_type TEXT NOT NULL,  -- uploaded_file, sent_message, deleted_file, created_api_key, etc.
    resource_id TEXT,
    resource_name TEXT,
    member_color TEXT,
    member_name TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- 2. Modify Existing Tables
-- ============================================================

-- profiles: add team member flags
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS is_team_member BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS team_owner_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;

-- files: add uploaded-by tracking
ALTER TABLE files ADD COLUMN IF NOT EXISTS uploaded_by_member_id UUID REFERENCES team_members(id) ON DELETE SET NULL;
ALTER TABLE files ADD COLUMN IF NOT EXISTS uploaded_by_color TEXT;
ALTER TABLE files ADD COLUMN IF NOT EXISTS uploaded_by_name TEXT;

-- messages: add sent-by tracking
ALTER TABLE messages ADD COLUMN IF NOT EXISTS sent_by_member_id UUID REFERENCES team_members(id) ON DELETE SET NULL;
ALTER TABLE messages ADD COLUMN IF NOT EXISTS sent_by_color TEXT;
ALTER TABLE messages ADD COLUMN IF NOT EXISTS sent_by_name TEXT;

-- ============================================================
-- 3. Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_team_members_owner_id ON team_members(owner_id);
CREATE INDEX IF NOT EXISTS idx_team_members_member_id ON team_members(member_id);
CREATE INDEX IF NOT EXISTS idx_team_members_aiveilix_email ON team_members(aiveilix_email);
CREATE INDEX IF NOT EXISTS idx_team_members_real_email ON team_members(real_email);
CREATE INDEX IF NOT EXISTS idx_team_bucket_access_team_member_id ON team_bucket_access(team_member_id);
CREATE INDEX IF NOT EXISTS idx_team_bucket_access_bucket_id ON team_bucket_access(bucket_id);
CREATE INDEX IF NOT EXISTS idx_team_activity_log_owner_id ON team_activity_log(owner_id);
CREATE INDEX IF NOT EXISTS idx_team_activity_log_team_member_id ON team_activity_log(team_member_id);
CREATE INDEX IF NOT EXISTS idx_team_activity_log_bucket_id ON team_activity_log(bucket_id);
CREATE INDEX IF NOT EXISTS idx_team_activity_log_created_at ON team_activity_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_team_owner_id ON profiles(team_owner_id);

-- ============================================================
-- 4. Triggers
-- ============================================================

-- Auto-update updated_at on team_members
CREATE OR REPLACE TRIGGER update_team_members_updated_at
    BEFORE UPDATE ON team_members
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-update updated_at on team_bucket_access
CREATE OR REPLACE TRIGGER update_team_bucket_access_updated_at
    BEFORE UPDATE ON team_bucket_access
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 5. Row-Level Security
-- ============================================================

ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_bucket_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_activity_log ENABLE ROW LEVEL SECURITY;

-- team_members: owner manages, member reads own
CREATE POLICY team_members_owner_all ON team_members
    FOR ALL USING (auth.uid() = owner_id);

CREATE POLICY team_members_member_select ON team_members
    FOR SELECT USING (auth.uid() = member_id);

-- team_bucket_access: owner manages via team_members join, member reads own
CREATE POLICY team_bucket_access_owner_all ON team_bucket_access
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM team_members tm
            WHERE tm.id = team_bucket_access.team_member_id
            AND tm.owner_id = auth.uid()
        )
    );

CREATE POLICY team_bucket_access_member_select ON team_bucket_access
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM team_members tm
            WHERE tm.id = team_bucket_access.team_member_id
            AND tm.member_id = auth.uid()
        )
    );

-- team_activity_log: owner reads all, member reads own
CREATE POLICY team_activity_log_owner_select ON team_activity_log
    FOR SELECT USING (auth.uid() = owner_id);

CREATE POLICY team_activity_log_owner_insert ON team_activity_log
    FOR INSERT WITH CHECK (auth.uid() = owner_id OR auth.uid() = member_id);

CREATE POLICY team_activity_log_member_select ON team_activity_log
    FOR SELECT USING (auth.uid() = member_id);
