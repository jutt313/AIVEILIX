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

    class Config:
        env_file = "../../.env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
