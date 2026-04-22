from fastapi.testclient import TestClient

from app.main import app
from app.schemas.auth import KakaoTokenResponse, KakaoUserProfile
from app.services.auth.kakao import kakao_auth_service

client = TestClient(app)


def test_get_kakao_login_url() -> None:
    response = client.get("/api/v1/auth/kakao/login")

    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "state" in data
    assert data["state"]


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
            kakao_account={"profile_nickname_needs_agreement": False},
        )

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

    response = client.get("/api/v1/auth/kakao/callback?code=test-code&state=abc123")

    assert response.status_code == 200
    assert response.json() == {
        "provider": "kakao",
        "state": "abc123",
        "token": {
            "token_type": "bearer",
            "access_token": "access-token",
            "expires_in": 21599,
            "refresh_token": "refresh-token",
            "refresh_token_expires_in": 5183999,
            "scope": "profile_nickname",
        },
        "user": {
            "id": 123456789,
            "connected_at": "2026-04-20T10:00:00Z",
            "properties": {"nickname": "codex"},
            "kakao_account": {"profile_nickname_needs_agreement": False},
        },
    }
