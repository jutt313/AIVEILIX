-- ============================================================
-- Migration 011: Usage tracking table + early-bird subscription columns
-- ============================================================

-- 1. Usage tracking table (for chat, MCP, bucket_chat metrics)
CREATE TABLE IF NOT EXISTS usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_type TEXT NOT NULL,       -- chat_messages, mcp_queries, bucket_chat
    period_type TEXT NOT NULL,       -- daily, hourly, minute
    period_key TEXT NOT NULL,        -- e.g. 2026-02-16, 2026-02-16-14, 2026-02-16-14-30
    count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Unique constraint for upserts
CREATE UNIQUE INDEX IF NOT EXISTS idx_usage_tracking_unique
    ON usage_tracking(user_id, metric_type, period_type, period_key);

-- Query index
CREATE INDEX IF NOT EXISTS idx_usage_tracking_lookup
    ON usage_tracking(user_id, metric_type, period_type);

-- RLS
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own usage tracking"
    ON usage_tracking FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage usage tracking"
    ON usage_tracking FOR ALL
    USING (true)
    WITH CHECK (true);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_usage_tracking_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER usage_tracking_updated_at
    BEFORE UPDATE ON usage_tracking
    FOR EACH ROW
    EXECUTE FUNCTION update_usage_tracking_updated_at();

-- Upsert function for incrementing metrics
CREATE OR REPLACE FUNCTION increment_usage_metric(
    p_user_id UUID,
    p_metric_type TEXT,
    p_period_type TEXT,
    p_period_key TEXT
)
RETURNS INTEGER AS $$
DECLARE
    current_count INTEGER;
BEGIN
    INSERT INTO usage_tracking (user_id, metric_type, period_type, period_key, count)
    VALUES (p_user_id, p_metric_type, p_period_type, p_period_key, 1)
    ON CONFLICT (user_id, metric_type, period_type, period_key)
    DO UPDATE SET count = usage_tracking.count + 1, updated_at = NOW()
    RETURNING count INTO current_count;

    RETURN current_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- 2. Add early-bird columns to subscriptions table
ALTER TABLE subscriptions
    ADD COLUMN IF NOT EXISTS subscribed_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS early_bird BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS early_bird_end TIMESTAMPTZ;


-- 3. Cleanup old usage_tracking rows (older than 90 days) - optional scheduled job
-- You can run this periodically via pg_cron or a backend task:
-- DELETE FROM usage_tracking WHERE created_at < NOW() - INTERVAL '90 days';
