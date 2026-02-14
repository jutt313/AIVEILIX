-- Migration: Add source to files table
-- Description: Distinguish uploaded vs created files

ALTER TABLE public.files
ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'uploaded';

UPDATE public.files
SET source = 'uploaded'
WHERE source IS NULL;

CREATE INDEX IF NOT EXISTS idx_files_source
ON public.files(bucket_id, source);

COMMENT ON COLUMN public.files.source IS 'Origin of file: uploaded | created';
