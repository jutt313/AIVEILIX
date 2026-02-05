from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    database_url: str

    # Gemini (optional)
    gemini_api_key: str = ""
    
    # DeepSeek API
    deepseek_api_key: str = ""

    # OpenAI API (for high-quality embeddings)
    openai_api_key: str = ""

    # Google Custom Search API (for web search in chat)
    google_search_api_key: str = ""
    google_search_cx: str = ""

    # App
    app_env: str = "development"
    app_secret_key: str = "change-me-in-production"

    # Error Tracking
    sentry_dsn: str = ""  # Get from sentry.io

    # Server
    backend_port: int = Field(default=7223, env="PORT")  # Render sets PORT automatically
    backend_url: str = "http://localhost:7223"  # Public base URL for MCP/OAuth full URLs
    frontend_url: str = "http://localhost:6677"
    cors_extra_origins: str = ""  # Comma-separated extra origins (e.g. for OAuth tools)

    # MCP Rate Limiting
    mcp_rate_limit_per_hour: int = 100
    mcp_rate_limit_window: int = 3600  # 1 hour in seconds

    # OAuth2 Settings
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_redirect_uri: str = "http://localhost:7223/oauth/callback"
    oauth_token_secret: str = "change-me-in-production-oauth-secret"
    oauth_token_expire_minutes: int = 60
    oauth_refresh_token_expire_days: int = 30

    # MCP Transport Settings
    mcp_enable_stdio: bool = True
    mcp_enable_http: bool = True
    mcp_http_port: int = 7223
    mcp_server_name: str = "aiveilix-mcp"
    mcp_server_version: str = "1.0.0"

    # Stripe Configuration
    stripe_publishable_key: str = ""
    stripe_secret_key: str = ""
    stripe_price_starter: str = ""
    stripe_price_pro: str = ""
    stripe_price_premium: str = ""
    stripe_webhook_secret: str = ""

    # SMTP Email Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@aiveilix.com"
    smtp_from_name: str = "AIveilix"

    # Plan Limits
    plan_limits: dict = {
        "free_trial": {
            "storage_gb": 1,
            "max_documents": 50,
            "max_file_size_mb": 10,
            "api_calls_per_day": 50
        },
        "starter": {
            "storage_gb": 3,
            "max_documents": 200,
            "max_file_size_mb": 25,
            "api_calls_per_day": 100
        },
        "pro": {
            "storage_gb": 10,
            "max_documents": -1,  # Unlimited
            "max_file_size_mb": 50,
            "api_calls_per_day": 1000
        },
        "premium": {
            "storage_gb": 50,
            "max_documents": -1,  # Unlimited
            "max_file_size_mb": 100,
            "api_calls_per_day": 5000
        }
    }

    class Config:
        env_file = "../../.env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
