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

### Backend (Render)

1. Create account at [Render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repository `jutt313/AIVEILIX`
4. Render will auto-detect `render.yaml` or manually configure:
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
5. Add all environment variables from `.env.example`:
   - Supabase credentials (URL, anon key, service role key, database URL)
   - AI API keys (DeepSeek, OpenAI, Gemini)
   - Google Search API keys (optional)
   - Set `APP_ENV=production`
   - Set `BACKEND_URL` to your Render URL (e.g., `https://aiveilix-backend.onrender.com`)
   - Set `FRONTEND_URL` to your Vercel URL
6. Deploy!

Render will auto-deploy on every push to `main`.

**Note**: Render automatically sets the `PORT` environment variable - the backend will use it automatically.

### Frontend (Vercel)

1. Create account at [Vercel.com](https://vercel.com)
2. New Project → Import from GitHub
3. Select this repository
4. Set root directory to `/frontend`
5. Add environment variables:
   - `VITE_API_URL` = Your Render backend URL (e.g., `https://aiveilix-backend.onrender.com`)
   - `VITE_SUPABASE_URL` = Your Supabase URL
   - `VITE_SUPABASE_ANON_KEY` = Your Supabase anon key
6. Deploy!

Vercel will auto-deploy on every push to `main`.

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
