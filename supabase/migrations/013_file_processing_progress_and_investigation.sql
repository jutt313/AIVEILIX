-- Migration: Add file processing progress + investigation linkage
-- Date: 2026-03-03

ALTER TABLE public.files
ADD COLUMN IF NOT EXISTS progress_stage TEXT NOT NULL DEFAULT 'queued',
ADD COLUMN IF NOT EXISTS progress_label TEXT,
ADD COLUMN IF NOT EXISTS progress_current INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS progress_total INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS progress_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS progress_meta JSONB NOT NULL DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS progress_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS investigation_conversation_id UUID NULL REFERENCES public.conversations(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS auto_summary_posted_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS auto_summary_error TEXT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'files_progress_percent_range_chk'
    ) THEN
        ALTER TABLE public.files
        ADD CONSTRAINT files_progress_percent_range_chk
        CHECK (progress_percent >= 0 AND progress_percent <= 100);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'files_progress_current_nonnegative_chk'
    ) THEN
        ALTER TABLE public.files
        ADD CONSTRAINT files_progress_current_nonnegative_chk
        CHECK (progress_current >= 0);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'files_progress_total_nonnegative_chk'
    ) THEN
        ALTER TABLE public.files
        ADD CONSTRAINT files_progress_total_nonnegative_chk
        CHECK (progress_total >= 0);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_files_progress_active
ON public.files(bucket_id, status, progress_updated_at DESC)
WHERE status IN ('pending', 'processing');

CREATE INDEX IF NOT EXISTS idx_files_investigation_conversation
ON public.files(investigation_conversation_id);

COMMENT ON COLUMN public.files.progress_stage IS 'Current processing stage (queued/downloading/extracting/image_ocr/chunking/embedding/storing/summarizing/finalizing/ready/failed).';
COMMENT ON COLUMN public.files.progress_label IS 'Human readable progress label shown in UI.';
COMMENT ON COLUMN public.files.progress_current IS 'Current step count within stage.';
COMMENT ON COLUMN public.files.progress_total IS 'Total step count within stage.';
COMMENT ON COLUMN public.files.progress_percent IS 'Overall processing percent (0-100).';
COMMENT ON COLUMN public.files.progress_meta IS 'Additional stage metadata for UI context.';
COMMENT ON COLUMN public.files.progress_updated_at IS 'Last progress update timestamp.';
COMMENT ON COLUMN public.files.investigation_conversation_id IS 'Conversation used for investigation auto-replies.';
COMMENT ON COLUMN public.files.auto_summary_posted_at IS 'Timestamp when auto investigation first reply was posted.';
COMMENT ON COLUMN public.files.auto_summary_error IS 'Last error while posting auto investigation reply.';
