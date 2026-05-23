import httpx

from app.core.config import settings


class SupabaseConfigError(Exception):
    """Supabase settings are missing."""


class SupabaseRequestError(Exception):
    """Supabase request failed."""


class SupabaseClient:
    def __init__(self) -> None:
        self.supabase_url = (settings.supabase_url or "").rstrip("/")
        self.service_role_key = settings.supabase_service_role_key

    def headers(self, prefer: str | None = None) -> dict[str, str]:
        if not self.supabase_url or not self.service_role_key:
            raise SupabaseConfigError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured."
            )

        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def auth_url(self, path: str) -> str:
        return f"{self._base_url()}/auth/v1{path}"

    def rest_url(self, path: str) -> str:
        return f"{self._base_url()}/rest/v1{path}"

    def raise_for_error(self, response: httpx.Response, message: str) -> None:
        if response.is_success:
            return

        raise SupabaseRequestError(f"{message}: {response.text}")

    def _base_url(self) -> str:
        if not self.supabase_url:
            raise SupabaseConfigError("SUPABASE_URL must be configured.")

        return self.supabase_url


supabase_client = SupabaseClient()
