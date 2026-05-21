from typing import Any
import httpx
from app.core.config import settings
from app.schemas.auth import KakaoUserProfile

class SupabaseUserSyncError(Exception):
    """Supabase user synchronization fails."""

class SupabaseUserService:
    def __init__(self) -> None:
        self.supabase_url = (settings.supabase_url or "").rstrip("/")
        self.service_role_key = settings.supabase_service_role_key

    def _headers(self, prefer: str | None = None) -> dict[str, str]:
        if not self.supabase_url or not self.service_role_key:
            raise SupabaseUserSyncError(
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

    def _auth_url(self, path: str) -> str:
        return f"{self.supabase_url}/auth/v1{path}"

    def _rest_url(self, path: str) -> str:
        return f"{self.supabase_url}/rest/v1{path}"

    async def save_kakao_user(self, user: KakaoUserProfile) -> str:
        email = self._extract_email(user)
        nickname = self._extract_nickname(user)
        profile_img = self._extract_profile_img(user)

        async with httpx.AsyncClient(timeout=10.0) as client:
            auth_user_id = await self._find_public_user_id_by_email(client, email)
            if auth_user_id is None:
                auth_user_id = await self._create_auth_user(
                    client=client,
                    email=email,
                    nickname=nickname,
                    profile_img=profile_img,
                    kakao_id=user.id,
                )

            await self._upsert_public_user(
                client=client,
                user_id=auth_user_id,
                email=email,
                nickname=nickname,
                profile_img=profile_img,
            )

        return auth_user_id

    def _extract_email(self, user: KakaoUserProfile) -> str:
        email = user.kakao_account.get("email")
        if not email:
            raise SupabaseUserSyncError(
                "Kakao account email is required to save the user. "
                "Request the account_email scope and enable email consent in Kakao."
            )
        return str(email)

    def _extract_nickname(self, user: KakaoUserProfile) -> str:
        kakao_profile = self._kakao_profile(user)
        nickname = user.properties.get("nickname") or kakao_profile.get("nickname")
        if not nickname:
            return f"kakao_{user.id}"
        return str(nickname)

    def _extract_profile_img(self, user: KakaoUserProfile) -> str | None:
        kakao_profile = self._kakao_profile(user)
        profile_img = (
            user.properties.get("profile_image")
            or kakao_profile.get("profile_image_url")
            or kakao_profile.get("thumbnail_image_url")
        )
        if profile_img is None:
            return None
        return str(profile_img)

    def _kakao_profile(self, user: KakaoUserProfile) -> dict[str, Any]:
        profile = user.kakao_account.get("profile")
        if isinstance(profile, dict):
            return profile
        return {}

    async def _find_public_user_id_by_email(
        self,
        client: httpx.AsyncClient,
        email: str,
    ) -> str | None:
        response = await client.get(
            self._rest_url("/users"),
            headers=self._headers(),
            params={
                "select": "id",
                "email": f"eq.{email}",
                "limit": "1",
            },
        )
        self._raise_for_supabase_error(response, "Failed to find public user")

        users = response.json()
        if users:
            return str(users[0]["id"])
        return None

    async def _create_auth_user(
        self,
        client: httpx.AsyncClient,
        email: str,
        nickname: str,
        profile_img: str | None,
        kakao_id: int,
    ) -> str:
        response = await client.post(
            self._auth_url("/admin/users"),
            headers=self._headers(),
            json={
                "email": email,
                "email_confirm": True,
                "user_metadata": {
                    "provider": "kakao",
                    "kakao_id": kakao_id,
                    "nickname": nickname,
                    "profile_img": profile_img,
                },
            },
        )
        if response.is_error:
            existing_user_id = await self._find_auth_user_id_by_email(client, email)
            if existing_user_id:
                return existing_user_id

            self._raise_for_supabase_error(response, "Failed to create Supabase auth user")

        auth_user = response.json()
        return str(auth_user["id"])

    async def _find_auth_user_id_by_email(
        self,
        client: httpx.AsyncClient,
        email: str,
    ) -> str | None:
        for page in range(1, 21):
            response = await client.get(
                self._auth_url("/admin/users"),
                headers=self._headers(),
                params={"page": str(page), "per_page": "1000"},
            )
            self._raise_for_supabase_error(response, "Failed to list Supabase auth users")

            data = response.json()
            if isinstance(data, dict):
                users = data.get("users", [])
            elif isinstance(data, list):
                users = data
            else:
                users = []
            for user in users:
                if user.get("email") == email:
                    return str(user["id"])

            if len(users) < 1000:
                return None

        return None

    async def _upsert_public_user(
        self,
        client: httpx.AsyncClient,
        user_id: str,
        email: str,
        nickname: str,
        profile_img: str | None,
    ) -> None:
        response = await client.post(
            self._rest_url("/users"),
            headers=self._headers("resolution=merge-duplicates"),
            params={"on_conflict": "id"},
            json={
                "id": user_id,
                "email": email,
                "nickname": nickname,
                "profile_img": profile_img,
            },
        )
        self._raise_supabase_error(response, "Failed to upsert public user")

    def _raise_supabase_error(self, response: httpx.Response, message: str) -> None:
        if response.is_success:
            return

        raise SupabaseUserSyncError(f"{message}: {response.text}")


supabase_user_service = SupabaseUserService()
