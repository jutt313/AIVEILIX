# Aiveilix — Tech Stack

> This document describes every technology used in Aiveilix, why it was chosen, its version, and where to find it.

---

## Frontend

| Technology | Purpose | Version | Link |
|---|---|---|---|
| **React** | UI framework | 18+ | [react.dev](https://react.dev/) |
| **Tailwind CSS** | Styling and theming | 3+ | [tailwindcss.com](https://tailwindcss.com/) |
| **React Router** | Page routing | 6+ | [reactrouter.com](https://reactrouter.com/) |
| **Axios** | HTTP requests to backend | latest | [axios-http.com](https://axios-http.com/) |

**Themes:** Light and dark mode supported via Tailwind. User preference saved to PostgreSQL.

---

## Backend

| Technology | Purpose | Version | Link |
|---|---|---|---|
| **Python** | Primary language | 3.11+ | [python.org](https://www.python.org/) |
| **FastAPI** | REST API framework | latest | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |
| **Uvicorn** | ASGI server | latest | [uvicorn.org](https://www.uvicorn.org/) |
| **Pydantic** | Data validation and serialization | v2+ | [docs.pydantic.dev](https://docs.pydantic.dev/) |

---

## File Processing

| Technology | Purpose | Link |
|---|---|---|
| **Docling** | Extracts text, structure, and coordinates from PDF, DOCX, PPTX, XLSX, images | [github.com/DS4SD/docling](https://github.com/DS4SD/docling) |
| **Gemini Flash API** | Visual understanding — analyzes images, charts, diagrams, and text inside visuals | [ai.google.dev](https://ai.google.dev/) |

**How they work together:**
- Docling handles all text extraction with exact (x, y) coordinates
- Gemini Flash handles all visual extraction with descriptions and text inside images
- A custom Python merger function in FastAPI combines both outputs into one Layout JSON Map

---

## RAG Pipeline

| Technology | Purpose | Link |
|---|---|---|
| **LlamaIndex** | Intelligent document chunking | [llamaindex.ai](https://www.llamaindex.ai/) |
| **BGE-M3** | Text embedding model (dense + sparse) | [huggingface.co/BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) |
| **CLIP** | Image embedding model | [github.com/openai/CLIP](https://github.com/openai/CLIP) |
| **BGE Reranker v2 M3** | Re-ranks top 50 results to top 5 for accuracy | [huggingface.co/BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) |

**Chunking settings:**
- Chunk size: 256 tokens
- Overlap: 50 tokens
- Tables: never split, kept whole
- Images: never chunked, stored as metadata attached to nearest text chunk

---

## Databases

| Database | Purpose | Link |
|---|---|---|
| **PostgreSQL** | All permanent structured data — users, buckets, files, auth, billing, teams | [postgresql.org](https://www.postgresql.org/) |
| **Qdrant** | Vector database for text and image embeddings | [qdrant.tech](https://qdrant.tech/) |
| **Redis** | Cache, sessions, and job queues | [redis.io](https://redis.io/) |

---

## File Storage

| Technology | Purpose | Link |
|---|---|---|
| **Cloudflare R2** | Raw file storage, processed files, Layout JSON Maps | [cloudflare.com/r2](https://www.cloudflare.com/developer-platform/r2/) |

**Why Cloudflare R2:**
- Zero egress fees — serving 1TB costs $0 in bandwidth
- $0.015/GB storage
- Free tier: 10GB storage + 10M reads/month
- S3-compatible API

---

## Authentication

| Technology | Purpose | Link |
|---|---|---|
| **python-jose** | JWT token creation and verification | [github.com/mpdavis/python-jose](https://github.com/mpdavis/python-jose) |
| **bcrypt** | Password hashing (cost factor 12) | [pypi.org/project/bcrypt](https://pypi.org/project/bcrypt/) |
| **pyotp** | TOTP two-factor authentication (Google Authenticator compatible) | [pypi.org/project/pyotp](https://pypi.org/project/pyotp/) |
| **Google OAuth 2.0** | One-click login with Google | [developers.google.com/identity](https://developers.google.com/identity) |
| **GitHub OAuth** | One-click login with GitHub | [docs.github.com/apps/oauth-apps](https://docs.github.com/en/apps/oauth-apps) |

---

## Agent Search

| Technology | Purpose | Link |
|---|---|---|
| **duckduckgo-search** | Free web search for the Aiveilix agent — no API key required | [github.com/deedy5/duckduckgo_search](https://github.com/deedy5/duckduckgo_search) |

---

## AI / LLM Options

The Aiveilix agent supports 4 LLM options. The user selects their preferred LLM in settings and provides their own API key. The selected LLM is used for all agent queries and document answers.

| LLM | Provider | Link |
|---|---|---|
| **Claude** | Anthropic | [anthropic.com](https://www.anthropic.com/) |
| **Gemini** | Google | [ai.google.dev](https://ai.google.dev/) |
| **GPT-4o** | OpenAI | [openai.com](https://openai.com/) |
| **Kimi** | Moonshot AI | [moonshot.cn](https://www.moonshot.cn/) |

**How it works:**
- User goes to settings and selects their preferred LLM
- User enters their API key for the selected LLM
- API key is stored securely in PostgreSQL (encrypted)
- All agent queries and document answers use the selected LLM

---

## Billing

| Technology | Purpose | Link |
|---|---|---|
| **Stripe** | Payment processing, subscriptions, billing | [stripe.com](https://stripe.com/) |

---

## Deployment

| Technology | Purpose | Link |
|---|---|---|
| **Docker** | Containerization | [docker.com](https://www.docker.com/) |
| **Google Cloud Run** | Serverless container deployment | [cloud.google.com/run](https://cloud.google.com/run) |
| **Google Cloud SQL** | Managed PostgreSQL | [cloud.google.com/sql](https://cloud.google.com/sql) |

---

## Full Stack Summary

```
User (Browser)
        |
        v
React + Tailwind CSS (Frontend)
        |
        v
FastAPI + Python 3.11 (Backend)
        |
   +————+————+————+————+
   |    |    |    |    |
   |    |    |    |    v
   |    |    |    |  Cloudflare R2
   |    |    |    |  (raw files + layouts)
   |    |    |    |
   |    |    |    v
   |    |    |  Redis
   |    |    |  (sessions + cache + queues)
   |    |    |
   |    |    v
   |    |  Qdrant
   |    |  (vector embeddings)
   |    |
   |    v
   |  PostgreSQL
   |  (all structured data)
   |
   v
File Processing:
  Docling → text extraction
  Gemini Flash → visual extraction
  Custom Merger → Layout JSON Map

RAG Pipeline:
  LlamaIndex → chunking
  BGE-M3 → text embeddings
  CLIP → image embeddings
  BGE Reranker → top 5 results

Agent:
  DuckDuckGo → web search
  Claude / Gemini / GPT-4o / Kimi → answer generation
```

---

*Document version: 1.0 — March 2026*
