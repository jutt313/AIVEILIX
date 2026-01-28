-- Migration: Create notifications table
-- Date: 2026-01-27
-- Description: Creates notifications table for user notifications (login, MCP run, create call, etc.)

-- Create notification types enum
CREATE TYPE notification_type AS ENUM (
    'login',
    'mcp_run',
    'file_uploaded',
    'file_processed',
    'bucket_created',
    'conversation_created',
    'api_key_created',
    'system',
    'error'
);

-- Create notifications table
CREATE TABLE public.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Notification content
    type notification_type NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    icon TEXT, -- Optional icon name (e.g., 'bell', 'check', 'error')
    
    -- Metadata
    metadata JSONB, -- Additional data (e.g., bucket_id, file_id, etc.)
    action_url TEXT, -- Optional URL to navigate to when clicked
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    read_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX idx_notifications_user_id_read ON public.notifications(user_id, is_read);
CREATE INDEX idx_notifications_created_at ON public.notifications(created_at DESC);
CREATE INDEX idx_notifications_type ON public.notifications(type);

-- Enable RLS
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Users can only see their own notifications
CREATE POLICY "Users can view own notifications" ON public.notifications
    FOR SELECT USING (auth.uid() = user_id);

-- Users can update their own notifications (mark as read, delete)
CREATE POLICY "Users can update own notifications" ON public.notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own notifications
CREATE POLICY "Users can delete own notifications" ON public.notifications
    FOR DELETE USING (auth.uid() = user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_notifications_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_notifications_updated_at
    BEFORE UPDATE ON public.notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_notifications_updated_at();

-- Function to auto-set read_at when is_read changes to true
CREATE OR REPLACE FUNCTION set_notification_read_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_read = TRUE AND OLD.is_read = FALSE THEN
        NEW.read_at = NOW();
    ELSIF NEW.is_read = FALSE THEN
        NEW.read_at = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-set read_at
CREATE TRIGGER set_notification_read_at
    BEFORE UPDATE ON public.notifications
    FOR EACH ROW
    EXECUTE FUNCTION set_notification_read_at();

-- Add comments for documentation
COMMENT ON TABLE public.notifications IS 'User notifications for various system events';
COMMENT ON COLUMN public.notifications.type IS 'Type of notification (login, mcp_run, file_uploaded, etc.)';
COMMENT ON COLUMN public.notifications.metadata IS 'Additional JSON data (bucket_id, file_id, etc.)';
COMMENT ON COLUMN public.notifications.action_url IS 'Optional URL to navigate when notification is clicked';
