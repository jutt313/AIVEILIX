-- Migration: Add metadata column to messages table for storing thinking content and AI metadata
-- This column stores JSON data including:
--   - thinking: AI's reasoning process
--   - phase: thinking/response
--   - model_config: model settings used

-- Add metadata JSONB column to messages table
ALTER TABLE messages ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT NULL;

-- Add comment for documentation
COMMENT ON COLUMN messages.metadata IS 'Stores AI metadata including thinking content, phase, and model configuration';

-- Create index for faster queries on metadata (GIN index for JSONB)
CREATE INDEX IF NOT EXISTS idx_messages_metadata ON messages USING GIN (metadata);
