from supabase import create_client, Client
from app.config import get_settings

settings = get_settings()

# Supabase client with service role (for backend operations)
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)

# Supabase client with anon key (for auth operations)
supabase_auth: Client = create_client(
    settings.supabase_url,
    settings.supabase_anon_key
)


def get_supabase() -> Client:
    return supabase


def get_supabase_auth() -> Client:
    return supabase_auth
