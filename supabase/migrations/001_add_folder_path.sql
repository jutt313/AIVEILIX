-- Migration: Add folder_path support to files table
-- Date: 2026-01-20
-- Description: Adds folder_path column to track folder structure when files are uploaded as part of a folder

-- Add folder_path column (nullable, so existing files work)
ALTER TABLE public.files 
ADD COLUMN IF NOT EXISTS folder_path TEXT;

-- Add index for better performance when filtering/grouping by folder
CREATE INDEX IF NOT EXISTS idx_files_folder_path 
ON public.files(bucket_id, folder_path) 
WHERE folder_path IS NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN public.files.folder_path IS 'Folder path within the bucket (e.g., "folder1/subfolder"). NULL for files uploaded individually (not in a folder).';
