# AIveilix - AI-Powered Knowledge Management Platform

An intelligent document vault system where users can upload documents (including images, PDFs, code files), organize them in "buckets" (vaults), and interact with their documents using AI-powered chat with semantic search capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.14+
- Node.js 18+
- PostgreSQL (via Supabase)
- OpenAI API key (for embeddings + vision)
- DeepSeek API key (for chat)

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

## 📦 Deployment

### Railway

1. Connect GitHub repository
2. Create new service for backend
3. Set environment variables from `.env.example`
4. Deploy!

### Render

1. Connect GitHub repository
2. Create Web Service for backend
3. Create Static Site for frontend (point to `frontend/dist`)
4. Set environment variables

## 🔧 Environment Variables

See `.env.example` for all required environment variables.

## 📚 Documentation

See `CLAUDE.md` for comprehensive architecture documentation.

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.14, PostgreSQL + pgvector
- **Frontend**: React 18, Vite, TailwindCSS 4
- **AI**: DeepSeek (chat), OpenAI (embeddings + vision)
- **Database**: Supabase (PostgreSQL + Storage)

## 📄 License

MIT
