import secrets
from urllib.parse import urlencode
import httpx
from app.core.config import settings
from app.schemas.auth import (
    KakaoLoginUrlResponse,
    KakaoTokenResponse,
    KakaoUserProfile,
)

class KakaoAuthError(Exception):
    """Kakao OAuth requests fail."""


class KakaoAuthService:
    authorize_url = "https://kauth.kakao.com/oauth/authorize" # Kakao 로그인 URL
    token_url = "https://kauth.kakao.com/oauth/token" # Kakao 토큰 발급 URL
    user_info_url = "https://kapi.kakao.com/v2/user/me" # Kakao 사용자 정보 조회 URL

    #로그인 URL 생성
    def build_login_response(
        self,
        state: str | None = None,
        scope: str | None = None,
    ) -> KakaoLoginUrlResponse:
        resolved_state = state or secrets.token_urlsafe(24)
        params = {
            "response_type": "code",
            "client_id": settings.kakao_rest_api_key,
            "redirect_uri": settings.kakao_redirect_uri,
            "state": resolved_state,
        }
        if scope:
            params["scope"] = scope

        return KakaoLoginUrlResponse(
            authorization_url=f"{self.authorize_url}?{urlencode(params)}",
            state=resolved_state,
        )

    #카카오에서 받은 인가코드를 토큰으로 교환
    async def exchange_code_for_token(self, code: str) -> KakaoTokenResponse:
        if not settings.kakao_rest_api_key:
            raise KakaoAuthError("KAKAO_REST_API_KEY is not configured.")

        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.kakao_rest_api_key,
            "redirect_uri": settings.kakao_redirect_uri,
            "code": code,
        }
        if settings.kakao_client_secret:
            payload["client_secret"] = settings.kakao_client_secret

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.token_url, data=payload)

        if response.is_error:
            raise KakaoAuthError(
                f"Failed to exchange Kakao authorization code: {response.text}"
            )

        return KakaoTokenResponse.model_validate(response.json())

    #사용자 정보 조회
    async def get_user_info(self, access_token: str) -> KakaoUserProfile:
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.user_info_url, headers=headers)

        if response.is_error:
            raise KakaoAuthError(f"Failed to retrieve Kakao user info: {response.text}")

        return KakaoUserProfile.model_validate(response.json())


kakao_auth_service = KakaoAuthService()
