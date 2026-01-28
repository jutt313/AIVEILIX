# Supabase Setup Guide for AIveilix

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project" / Sign in
3. Click "New Project"
4. Fill in:
   - **Name**: `aiveilix`
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your users
5. Click "Create new project"
6. Wait for project to initialize (~2 minutes)

## Step 2: Get Your Credentials

### API Keys
1. Go to **Settings** → **API**
2. Copy these values to your `.env` file:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` key → `SUPABASE_ANON_KEY`
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY`

### Database URL
1. Go to **Settings** → **Database**
2. Under "Connection string", select "URI"
3. Copy the connection string → `DATABASE_URL`
4. Replace `[YOUR-PASSWORD]` with your database password

## Step 3: Enable pgvector Extension

1. Go to **Database** → **Extensions**
2. Search for `vector`
3. Enable the **vector** extension

## Step 4: Run the Schema

### Option A: Supabase Dashboard (Recommended)
1. Go to **SQL Editor**
2. Click "New query"
3. Copy entire contents of `schema.sql`
4. Paste into the editor
5. Click "Run"

### Option B: Using psql
```bash
psql $DATABASE_URL -f supabase/schema.sql
```

## Step 5: Set Up Storage Bucket

1. Go to **Storage**
2. Click "New bucket"
3. Create bucket named `files`
4. Set to **Private** (not public)
5. Enable RLS policies:

```sql
-- Allow users to upload to their own folder
CREATE POLICY "Users can upload own files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Allow users to read own files
CREATE POLICY "Users can read own files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Allow users to delete own files
CREATE POLICY "Users can delete own files" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'files' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );
```

## Step 6: Configure Auth

1. Go to **Authentication** → **Providers**
2. Email is enabled by default
3. Optional: Enable Google, GitHub, etc.

### Auth Settings
1. Go to **Authentication** → **URL Configuration**
2. Set your site URL for redirects

## Step 7: Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API key"
3. Copy the key → `GEMINI_API_KEY` in your `.env`

## Your .env File Should Look Like:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:yourpassword@db.xxxxx.supabase.co:5432/postgres
GEMINI_API_KEY=AIza...
APP_ENV=development
APP_SECRET_KEY=your-random-secret-key
```

## Verify Setup

Run this query in SQL Editor to verify tables exist:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

You should see:
- actions
- api_keys
- buckets
- categories
- chunks
- conversations
- files
- messages
- profiles
- summaries

## Done!

Your database is ready. The schema includes:
- ✅ 10 tables with full RLS security
- ✅ pgvector for semantic search
- ✅ Full-text search indexes
- ✅ Auto-updating timestamps
- ✅ Bucket stats tracking
- ✅ Search functions (keyword, semantic, full scan)
