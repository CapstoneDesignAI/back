from supabase import Client, create_client

from app.core.config import settings


class SupabaseConfigError(Exception):
    """Raised when Supabase settings are missing."""


_supabase: Client | None = None


def get_supabase() -> Client:
    global _supabase

    if _supabase is not None:
        return _supabase

    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise SupabaseConfigError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured."
        )

    _supabase = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )
    return _supabase
