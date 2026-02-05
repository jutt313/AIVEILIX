# AIveilix

## What It Is

AIveilix is an AI-powered knowledge management platform. Upload your documents, organize them in buckets (vaults), and chat with an AI that has full access to your files.

---

## How It Works

### 1. **Upload Documents**
- PDFs, images, code files, Word docs, text files
- Drag-drop files or entire folders
- Organized in "buckets" (separate vaults for different projects/topics)

### 2. **AI Processing**
- **Text extraction**: Reads PDFs, DOCX, code files
- **Image analysis**: Uses GPT-4o Vision to extract text and describe images
- **Chunking**: Breaks documents into 150-word chunks with 50-word overlap
- **Embeddings**: Converts chunks to 3072-dimensional vectors (OpenAI `text-embedding-3-large`)
- **Semantic search**: Finds relevant content using vector similarity (pgvector)

### 3. **Chat with AI**
- Ask questions about your documents
- AI searches your files semantically (meaning-based, not just keywords)
- Cites sources with file names and page numbers
- Can search the web if needed (Google Custom Search)
- Streams responses in real-time

### 4. **Smart Features**
- **Web search integration**: AI auto-detects when it needs current info
- **Stop generation**: Cancel AI responses mid-stream
- **Conversation history**: Saves all chats per bucket
- **File selection**: Choose specific files for context (@mentions)
- **Dark/Light mode**: Full theme support

---

## Tech Stack

### Backend
- **FastAPI** (Python 3.14) - REST API
- **Supabase** - PostgreSQL + Auth + Storage
- **pgvector** - Vector similarity search
- **DeepSeek** - Chat AI ($0.14/1M input tokens)
- **OpenAI** - Embeddings + Vision
- **Google Gemini** - Fallback AI

### Frontend
- **React 18** + **Vite**
- **TailwindCSS 4** - Styling
- **Axios** - API calls

### Infrastructure
- **Render** - Hosting (backend + frontend)
- **Supabase Cloud** - Database + Auth + Storage

---

## Key Capabilities

| Feature | Description |
|---------|-------------|
| **Semantic Search** | Finds relevant content by meaning, not just keywords |
| **Multi-format Support** | PDFs, images, code, DOCX, TXT, MD, JSON, etc. |
| **Vision AI** | Extracts text from images and embedded PDF images |
| **Web Search** | AI can search Google when needed |
| **Source Citations** | AI cites which files it used |
| **Streaming Responses** | Real-time AI output |
| **Conversation Memory** | Saves chat history per bucket |
| **MCP Protocol** | API for external integrations |

---

## Use Cases

1. **Research**: Upload papers, chat to find connections
2. **Code Documentation**: Upload codebase, ask how it works
3. **Legal/Compliance**: Search contracts, policies, regulations
4. **Education**: Upload textbooks, lecture notes, ask questions
5. **Business Intelligence**: Upload reports, analyze trends
6. **Personal Knowledge Base**: Store notes, articles, references

---

## Architecture

```
User → Frontend (React)
  ↓
Backend (FastAPI)
  ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   Supabase      │   AI Services   │   Web Search    │
│  - PostgreSQL   │  - DeepSeek     │  - Google API   │
│  - Auth         │  - OpenAI       │                 │
│  - Storage      │  - Gemini       │                 │
│  - pgvector     │                 │                 │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## Data Flow

1. **Upload**: File → Supabase Storage
2. **Process**: Extract text → Generate embeddings → Store in DB
3. **Chat**: User question → Semantic search → Build context → AI response
4. **Stream**: AI generates response → Stream to frontend → Display

---

## Security

- **Row-level security (RLS)**: Users only see their own data
- **JWT authentication**: Supabase Auth tokens
- **API key support**: For MCP integrations
- **Rate limiting**: 200 req/min default, 100 req/hour for MCP
- **Password verification**: Required for account deletion

---

## Cost Efficiency

**Per active user/month (5GB storage, 100 chats):**
- Supabase: ~$0.60
- DeepSeek AI: ~$0.06
- OpenAI (embeddings + vision): ~$0.25
- **Total: ~$0.91/user/month**

DeepSeek's pricing makes this extremely affordable compared to GPT-4.

---

## Current Status

**Production-ready features:**
- ✅ User authentication (signup, login, password reset)
- ✅ Bucket management (create, delete, organize)
- ✅ File upload (multi-format support)
- ✅ AI chat with semantic search
- ✅ Web search integration
- ✅ Source citations
- ✅ Streaming responses
- ✅ Dark/Light themes
- ✅ Conversation history
- ✅ MCP protocol support

**Not implemented:**
- ❌ Sharing buckets with other users
- ❌ Collaborative editing
- ❌ Mobile apps
- ❌ Advanced analytics dashboard

---

## Deployment

- **Backend**: Render Web Service (Starter plan, $7/month)
- **Frontend**: Render Static Site (Free)
- **Database**: Supabase (Pay-as-you-go)
- **Domain**: Custom domain support via Render

---

## Summary

AIveilix is a practical tool for anyone who needs to search, analyze, or chat with their documents using AI. It's built with modern, cost-efficient technologies and focuses on semantic understanding rather than simple keyword matching.

No marketing fluff. Just a working knowledge management system.
