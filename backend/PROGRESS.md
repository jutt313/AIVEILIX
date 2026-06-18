# AIveilix Backend — Progress

## Status: Infra Connected ✅

---

## Structure

```
backend/
├── app/
│   ├── main.py              ✅ FastAPI app, CORS, lifespan, port 4565
│   ├── config.py            ✅ all settings via pydantic-settings
│   ├── database.py          ✅ PostgreSQL async (SQLAlchemy + asyncpg) + connection check
│   ├── valkey.py            ✅ Valkey connection (Redis-compatible)
│   ├── qdrant_client.py     ✅ Qdrant client factory (local path or host/port)
│   ├── api/
│   │   └── v1/
│   │       ├── router.py    ✅ all routers registered
│   │       └── endpoints/
│   │           ├── auth.py          ✅ 13 routes stubbed
│   │           ├── users.py         ✅ 5 routes stubbed
│   │           ├── buckets.py       ✅ 8 routes stubbed
│   │           ├── files.py         ✅ 7 routes stubbed
│   │           ├── categories.py    ✅ 3 routes stubbed
│   │           ├── search.py        ✅ 2 routes stubbed
│   │           ├── conversations.py ✅ 5 routes stubbed
│   │           ├── notifications.py ✅ 3 routes stubbed
│   │           ├── billing.py       ✅ 5 routes stubbed
│   │           └── mcp.py           ✅ 2 routes stubbed
│   ├── models/              ⏳ empty — DB models next
│   ├── schemas/             ⏳ empty — Pydantic schemas next
│   ├── services/            ✅ dependency health service added
│   └── core/                ⏳ empty — security/utils next
├── run.py                   ✅ uvicorn entry point
├── Dockerfile               ✅ port 4565
├── requirements.txt         ✅ all packages listed
└── .env.example             ✅ all env vars documented
```

---

## Port
- `4565`
- Docs: `http://localhost:4565/docs` (dev only)
- Health: `http://localhost:4565/health`

---

## Tech Stack

| Layer | Tech |
|---|---|
| Framework | FastAPI 0.115.6 |
| Server | Uvicorn |
| Language | Python 3.11 |
| PostgreSQL | SQLAlchemy async + asyncpg |
| Cache/Queue | Valkey (Redis-compatible) via redis-py |
| Vectors | Qdrant client |
| File Storage | Cloudflare R2 (boto3 S3-compatible) |
| Auth | python-jose (JWT) + bcrypt + pyotp (2FA) |
| File Processing | Docling + Gemini Flash |
| Embeddings | BGE-M3 (text) + CLIP (images) via FlagEmbedding |
| Web Search | DuckDuckGo search |
| LLM | Claude (Anthropic) — backend decision, users don't pick |
| Billing | Stripe |

---

## All API Routes

### Auth — `/v1/auth`
| Method | Route | Status |
|---|---|---|
| POST | `/register` | ⏳ stub |
| POST | `/verify-email` | ⏳ stub |
| POST | `/login` | ⏳ stub |
| POST | `/2fa/verify` | ⏳ stub |
| POST | `/2fa/enable` | ⏳ stub |
| POST | `/2fa/confirm` | ⏳ stub |
| POST | `/2fa/disable` | ⏳ stub |
| POST | `/refresh` | ⏳ stub |
| POST | `/logout` | ⏳ stub |
| POST | `/forgot-password` | ⏳ stub |
| POST | `/reset-password` | ⏳ stub |
| POST | `/google` | ⏳ stub |
| POST | `/github` | ⏳ stub |

### User — `/v1/user`
| Method | Route | Status |
|---|---|---|
| GET | `/profile` | ⏳ stub |
| PUT | `/profile` | ⏳ stub |
| PUT | `/avatar` | ⏳ stub |
| PUT | `/password` | ⏳ stub |
| DELETE | `/account` | ⏳ stub |

### Buckets — `/v1/buckets`
| Method | Route | Status |
|---|---|---|
| GET | `` | ⏳ stub |
| POST | `` | ⏳ stub |
| GET | `/{bucket_id}` | ⏳ stub |
| PUT | `/{bucket_id}` | ⏳ stub |
| DELETE | `/{bucket_id}` | ⏳ stub |
| GET | `/{bucket_id}/mcp-url` | ⏳ stub |
| POST | `/{bucket_id}/mcp-url/regenerate` | ⏳ stub |
| POST | `/{bucket_id}/mcp-url/revoke` | ⏳ stub |

### Files — `/v1/buckets/{bucket_id}/files`
| Method | Route | Status |
|---|---|---|
| POST | `` | ⏳ stub |
| GET | `` | ⏳ stub |
| GET | `/{file_id}` | ⏳ stub |
| DELETE | `/{file_id}` | ⏳ stub |
| GET | `/{file_id}/summary` | ⏳ stub |
| GET | `/{file_id}/layout` | ⏳ stub |
| GET | `/{file_id}/chunks` | ⏳ stub |

### Categories — `/v1/buckets/{bucket_id}/categories`
| Method | Route | Status |
|---|---|---|
| GET | `` | ⏳ stub |
| POST | `` | ⏳ stub |
| DELETE | `/{category_id}` | ⏳ stub |

### Search — `/v1/buckets/{bucket_id}`
| Method | Route | Status |
|---|---|---|
| POST | `/search` | ⏳ stub |
| POST | `/query` | ⏳ stub |

### Conversations — `/v1/buckets/{bucket_id}/conversations`
| Method | Route | Status |
|---|---|---|
| GET | `` | ⏳ stub |
| POST | `` | ⏳ stub |
| DELETE | `/{conversation_id}` | ⏳ stub |
| GET | `/{conversation_id}/messages` | ⏳ stub |
| POST | `/{conversation_id}/messages` | ⏳ stub |

### Notifications — `/v1/notifications`
| Method | Route | Status |
|---|---|---|
| GET | `` | ⏳ stub |
| PUT | `/read-all` | ⏳ stub |
| DELETE | `/{notification_id}` | ⏳ stub |

### Billing — `/v1/billing`
| Method | Route | Status |
|---|---|---|
| GET | `/plan` | ⏳ stub |
| POST | `/upgrade` | ⏳ stub |
| POST | `/cancel` | ⏳ stub |
| GET | `/history` | ⏳ stub |
| POST | `/webhook` | ⏳ stub |

### MCP — `/v1/mcp`
| Method | Route | Status |
|---|---|---|
| GET | `/bucket/{mcp_token}` | ⏳ stub |
| GET | `/account/{account_mcp_token}` | ⏳ stub |

---

## How to Run

```bash
cd backend
cp .env.example .env
pip3 install -r requirements.txt
python3 run.py
```

---

## Verified Infra

- PostgreSQL connection verified through backend app code
- Qdrant connection verified through backend app code
- Valkey connection verified through backend app code
- `/health` now reports live dependency status instead of a static response

---

## Next Steps

- [ ] PostgreSQL models (SQLAlchemy) — all tables
- [ ] Pydantic schemas — request/response models
- [ ] Auth logic — register, login, JWT, 2FA, OAuth
- [ ] File upload → Cloudflare R2
- [ ] File processing — Docling + Gemini Flash + Layout JSON
- [ ] RAG pipeline — chunking, BGE-M3, CLIP, Qdrant
- [ ] Hybrid search + BGE Reranker
- [ ] Agent + LLM integration (Claude)
- [ ] MCP server implementation
- [ ] Stripe billing
- [ ] Alembic migrations
