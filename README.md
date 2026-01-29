# AIveilix - AI-Powered Knowledge Management Platform

An intelligent document vault system where users can upload documents (including images, PDFs, code files), organize them in "buckets" (vaults), and interact with their documents using AI-powered chat with semantic search capabilities.

## 🚀 Tech Stack

- **Backend**: FastAPI (Python 3.14) on port 7223
- **Frontend**: React 18 + Vite on port 6677
- **Database**: PostgreSQL + pgvector (via Supabase)
- **AI**: DeepSeek (chat), OpenAI (embeddings + vision), Google Gemini (fallback)
- **Styling**: TailwindCSS 4
- **Authentication**: Supabase Auth (JWT tokens)
- **Storage**: Supabase Storage (file uploads)

## 📋 Prerequisites

- Python 3.14+
- Node.js 18+
- Supabase account
- API keys: DeepSeek, OpenAI, Google Search (optional)

## 🛠️ Local Development

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Backend runs on `http://localhost:7223`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:6677`

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# AI APIs
DEEPSEEK_API_KEY=sk-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...  # Optional

# Google Search (optional)
GOOGLE_SEARCH_API_KEY=...
GOOGLE_SEARCH_CX=...

# App
APP_ENV=development
BACKEND_PORT=7223
FRONTEND_URL=http://localhost:6677
```

## 🚢 Deployment

### Backend + Frontend (Render)

Both backend and frontend are defined in `render.yaml`. Deploy once from Render:

1. Create account at [Render.com](https://render.com)
2. New → **Blueprint** (or connect repo and use "Apply render.yaml")
3. Connect GitHub repository and select this repo
4. Render creates two services from `render.yaml`:
   - **aiveilix-backend** (Web Service, Starter plan) – API
   - **aiveilix-frontend** (Static Site, free) – React app
5. When prompted, set environment variables:
   - **Backend**: All from `.env.example` (Supabase, API keys, etc.). Set `APP_ENV=production`, `FRONTEND_URL=https://aiveilix-frontend.onrender.com`
   - **Frontend**: Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` (VITE_API_URL and VITE_APP_URL are in the Blueprint)
6. Deploy!

Both services auto-deploy on push to `main`. Frontend: `https://aiveilix-frontend.onrender.com`, Backend: `https://aiveilix-backend.onrender.com`.

**Note**: Backend uses Render’s `PORT` automatically. Backend is on **Starter** plan ($7/mo); frontend static site is **free**.

### Remove from Vercel (if you used it before)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Open the AIveilix (or your project) deployment
3. **Settings** → **General** → scroll to **Delete Project** and delete, or **Settings** → **Git** → disconnect the repo
4. No need to delete the repo on GitHub; just stop using Vercel for this app.

### Database Setup

1. Create Supabase project
2. Enable pgvector extension: `CREATE EXTENSION vector;`
3. Run `supabase/schema.sql` in SQL editor
4. Run migrations in order from `supabase/migrations/`
5. Create storage bucket named "files" (private)
6. Add storage RLS policies

## 📁 Project Structure

```
AIveilix/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── routers/   # API endpoints
│   │   ├── services/  # Business logic
│   │   └── models/    # Pydantic models
│   └── run.py         # Entry point
├── frontend/          # React frontend
│   ├── src/
│   │   ├── pages/     # Page components
│   │   ├── components/ # Reusable components
│   │   └── services/   # API client
│   └── vite.config.js
├── supabase/          # Database schema & migrations
└── .env.example       # Environment template
```

## 🔑 Key Features

- **File Processing**: Images (GPT-4 Vision), PDFs, DOCX, CSV, 50+ code types
- **Semantic Search**: 3072-dim embeddings with pgvector
- **AI Chat**: DeepSeek-powered chat with document context
- **MCP Protocol**: ChatGPT/Cursor integration
- **OAuth2**: Secure API access
- **Notifications**: Real-time user notifications

## 📚 Documentation

See `CLAUDE.md` for comprehensive architecture documentation.

## 📝 License

MIT
