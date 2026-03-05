-- Migration: Investigation event timeline for live canvas UX
-- Date: 2026-03-03

CREATE TABLE IF NOT EXISTS public.investigation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES public.files(id) ON DELETE CASCADE,
    bucket_id UUID NOT NULL REFERENCES public.buckets(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    event_type TEXT NOT NULL,
    stage TEXT NULL,
    label TEXT NOT NULL,
    current INTEGER NOT NULL DEFAULT 0,
    total INTEGER NOT NULL DEFAULT 0,
    percent NUMERIC(5,2) NOT NULL DEFAULT 0,
    meta JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'investigation_events_percent_range_chk'
    ) THEN
        ALTER TABLE public.investigation_events
        ADD CONSTRAINT investigation_events_percent_range_chk
        CHECK (percent >= 0 AND percent <= 100);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'investigation_events_current_nonnegative_chk'
    ) THEN
        ALTER TABLE public.investigation_events
        ADD CONSTRAINT investigation_events_current_nonnegative_chk
        CHECK (current >= 0);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'investigation_events_total_nonnegative_chk'
    ) THEN
        ALTER TABLE public.investigation_events
        ADD CONSTRAINT investigation_events_total_nonnegative_chk
        CHECK (total >= 0);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_investigation_events_bucket_created
ON public.investigation_events(bucket_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_investigation_events_file_created
ON public.investigation_events(file_id, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_investigation_events_created_at
ON public.investigation_events(created_at DESC);

COMMENT ON TABLE public.investigation_events IS 'Append-only investigation timeline events for live processing canvas.';
COMMENT ON COLUMN public.investigation_events.event_type IS 'One of: stage, counter, note, error, complete.';
COMMENT ON COLUMN public.investigation_events.stage IS 'Canonical stage: queued/downloading/extracting/image_ocr/chunking/embedding/storing/summarizing/finalizing/ready/failed.';
COMMENT ON COLUMN public.investigation_events.meta IS 'Additional event details used by investigation canvas.';

CREATE OR REPLACE FUNCTION public.cleanup_old_investigation_events(retain_days INTEGER DEFAULT 14)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.investigation_events
    WHERE created_at < NOW() - make_interval(days => retain_days);

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;
