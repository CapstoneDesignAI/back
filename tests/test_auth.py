import base64
import json
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.auth import KakaoTokenResponse, KakaoUserProfile
from app.services.auth.kakao import kakao_auth_service
from app.services.auth.supabase_users import supabase_user_service

client = TestClient(app)

def test_get_kakao_login_url() -> None:
    response = client.get("/api/v1/auth/kakao")

    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "state" in data
    assert data["state"]
    assert "account_email" in data["authorization_url"]


def test_kakao_callback(monkeypatch) -> None:
    async def fake_exchange_code_for_token(code: str) -> KakaoTokenResponse:
        assert code == "test-code"
        return KakaoTokenResponse(
            token_type="bearer",
            access_token="access-token",
            expires_in=21599,
            refresh_token="refresh-token",
            refresh_token_expires_in=5183999,
            scope="profile_nickname",
        )

    async def fake_get_user_info(access_token: str) -> KakaoUserProfile:
        assert access_token == "access-token"
        return KakaoUserProfile(
            id=123456789,
            connected_at="2026-04-20T10:00:00Z",
            properties={"nickname": "codex"},
            kakao_account={
                "email": "codex@example.com",
                "profile_nickname_needs_agreement": False,
            },
        )

    async def fake_save_kakao_user(user: KakaoUserProfile) -> str:
        assert user.id == 123456789
        return "00000000-0000-0000-0000-000000000000"

    monkeypatch.setattr(
        kakao_auth_service,
        "exchange_code_for_token",
        fake_exchange_code_for_token,
    )
    monkeypatch.setattr(
        kakao_auth_service,
        "get_user_info",
        fake_get_user_info,
    )
    monkeypatch.setattr(
        supabase_user_service,
        "save_kakao_user",
        fake_save_kakao_user,
    )

    response = client.get(
        "/api/v1/auth/kakao/callback?code=test-code&state=abc123",
        follow_redirects=False,
    )

    assert response.status_code == 307
    location = response.headers["location"]
    query = parse_qs(urlparse(location).query)
    access_token = query["accessToken"][0]
    refresh_token = query["refreshToken"][0]

    assert access_token != "access-token"
    assert refresh_token != "refresh-token"

    access_payload = _decode_jwt_payload(access_token)
    refresh_payload = _decode_jwt_payload(refresh_token)
    assert access_payload["sub"] == "00000000-0000-0000-0000-000000000000"
    assert access_payload["type"] == "access"
    assert access_payload["email"] == "codex@example.com"
    assert access_payload["kakao_id"] == 123456789
    assert refresh_payload["sub"] == "00000000-0000-0000-0000-000000000000"
    assert refresh_payload["type"] == "refresh"


def _decode_jwt_payload(token: str) -> dict:
    payload = token.split(".")[1]
    padded_payload = payload + "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(padded_payload))
