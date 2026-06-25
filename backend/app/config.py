from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_ENV_FILE),
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = "development"
    secret_key: str = "change-this-secret"
    admin_api_key: str = ""   # secret required before emailing an admin login code
    admin_emails: str = ""    # comma-separated emails granted admin (in addition to users.is_admin)
    admin_phone: str = ""     # reserved for SMS admin codes once a provider is added
    port: int = 4565

    # JWT
    access_token_expire_minutes: int = 1440   # 24 hours
    refresh_token_expire_days: int = 30
    algorithm: str = "HS256"

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/aiveilix"

    # Qdrant — resolution order: qdrant_url (cloud) → qdrant_path (embedded) → host:port (server)
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_path: str | None = None
    # LlamaIndex path is disabled: pipeline v3 embeds with Voyage and the native
    # Qdrant path below uses the matching Voyage query embedding.
    llamaindex_enabled: bool = False
    llamaindex_hybrid_alpha: float = 0.5

    # RAG improvements (can be toggled per environment)
    reranker_enabled: bool = True          # Voyage rerank-2.5 after Qdrant retrieval
    query_expansion_enabled: bool = True   # LLM multi-query expansion before retrieval
    # Adaptive retrieval: try a cheap, narrow search first; only escalate to the
    # wide multi-query sweep (rephrasings + 200 candidates) when the fast pass is
    # not confident. Easy questions answer fast; weak matches search harder.
    retrieval_adaptive_enabled: bool = True
    retrieval_fast_candidate_limit: int = 40  # candidate set size for the fast pass
    # Image search is disabled: pipeline v3 indexes visual elements as text chunks
    # (no separate CLIP image_chunks collection).
    image_search_enabled: bool = False
    context_window_size: int = 1           # ±N chunk neighbors to expand each retrieved chunk
    retrieval_dedup_enabled: bool = True   # collapse near-identical chunks/images at query time
    retrieval_dedup_threshold: float = 0.93  # min similarity to drop a near-duplicate result

    @field_validator("qdrant_path", mode="before")
    @classmethod
    def _normalize_qdrant_path(cls, v: object) -> str | None:
        if v is None or v == "":
            return None
        if isinstance(v, str):
            s = v.strip()
            return s or None
        return str(v)

    # Valkey
    valkey_url: str = "redis://127.0.0.1:6380"

    # Cloudflare R2
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "aiveilix"
    r2_public_url: str = ""

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""

    # Gemini (file visual processing + optional LLM)
    gemini_api_key: str = ""
    gemini_visual_model: str = "gemini-3.1-flash-lite"   # pipeline v3 visual understanding

    # LLM backend choice
    # Supported values: auto, claude, gemini, openai, deepseek, kimi, gpt4o
    llm_provider: str = "auto"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    moonshot_api_key: str = ""
    moonshot_base_url: str = "https://api.moonshot.ai/v1"
    moonshot_visual_model: str = "moonshot-v1-8k-vision-preview"  # pipeline v3 visual understanding
    minimax_api_key: str = ""
    minimax_base_url: str = "https://api.minimaxi.chat/v1"
    minimax_model: str = "abab6.5s-chat"
    processing_v3_ai_summary: bool = True  # When True, use LLM (Kimi/Gemini) for rich doc-level summaries. Adds ~30-60s per file but produces much more detailed summaries that MCP clients can rely on.

    # Pipeline v3 — API-based document processing
    mistral_api_key: str = ""        # Mistral OCR
    voyage_api_key: str = ""         # Voyage embeddings + rerank
    # MCP/lite tier uses voyage-3-lite (512-dim) instead of voyage-3-large (1024-dim).
    voyage_lite_model: str = "voyage-3-lite"
    # Token overlap added between consecutive chunks' embedded text only
    # (display content stays clean). Improves retrieval recall across cuts.
    lite_chunk_overlap_tokens: int = 40
    # (visual understanding uses gemini_visual_model above)

    # Pipeline v3 — parallelism / throughput
    # Files in a batch process concurrently (each is mostly network I/O), and the
    # heavy per-page / per-batch steps fan out instead of running one at a time.
    file_processing_concurrency: int = 8   # max files processed at once, in-process
    ocr_concurrency: int = 12              # max concurrent Mistral OCR calls per file
    embed_concurrency: int = 4             # max concurrent Voyage embed batches per file

    # Dedicated processing worker (optional — Phase 3). When both the queue and the
    # worker URL are set, uploads enqueue one Cloud Tasks HTTP task per file to a
    # separate Cloud Run worker (true horizontal parallelism, dedicated CPU, scales
    # to zero). When unset, files process in-process via the concurrency above.
    processing_queue: str = ""             # Cloud Tasks queue id, e.g. "file-processing"
    processing_worker_url: str = ""        # base URL of the worker service
    processing_secret: str = ""            # shared secret guarding the internal endpoint
    gcp_project: str = ""                  # project id for Cloud Tasks
    gcp_region: str = "us-central1"        # Cloud Tasks queue location

    # Pipeline v3 — ingestion cleanup (runs before summary/export/chunking)
    ingest_dedup_enabled: bool = True            # collapse near-identical elements before export/chunk
    ingest_dedup_threshold: float = 0.90         # min similarity to treat two elements as duplicates
    name_reconcile_enabled: bool = True          # canonicalize obvious spelling slips + flag conflicts
    name_canonicalize_min_occurrences: int = 3   # dominant spelling must appear >= this many times to auto-fix
    name_canonicalize_ratio: float = 3.0         # dominant must outweigh a variant by this ratio to auto-fix
    name_variant_min_ratio: float = 0.80         # min char-similarity for two spellings to be the same entity

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_individual: str = ""   # recurring price ID for Individual ($15/mo)
    stripe_price_team: str = ""         # recurring price ID for Team ($49/mo)
    stripe_price_mcp: str = ""          # recurring price ID for MCP ($12/mo)

    # Frontend
    frontend_url: str = "http://localhost:5173"
    frontend_allowed_origins: str = ""
    vite_dev_port: int = 5173

    @property
    def cors_origins(self) -> list[str]:
        origins = [self.frontend_url, *self.frontend_allowed_origins.split(",")]
        if self.app_env == "development":
            origins.extend([
                f"http://localhost:{self.vite_dev_port}",
                f"http://127.0.0.1:{self.vite_dev_port}",
            ])
        out: list[str] = []
        seen: set[str] = set()
        for origin in origins:
            cleaned = origin.strip().rstrip("/")
            if cleaned and cleaned not in seen:
                out.append(cleaned)
                seen.add(cleaned)
        return out

    # MCP
    mcp_base_url: str = "https://mcp.aiveilix.com"

    # Agentic RAG loop — bounded planner-executor for multi-part questions
    agentic_rag_loop_enabled: bool = False
    agentic_rag_loop_max_subquestions: int = 8
    agentic_rag_loop_max_retries_per_subquestion: int = 1
    agentic_rag_loop_doc_limit_per_subquestion: int = 4
    agentic_rag_loop_web_limit_per_subquestion: int = 3
    agentic_rag_loop_max_total_searches: int = 30

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "info@aiveilix.com"
    smtp_from_name: str = "AIveilix"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
