import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings

class TokenService:
    def create_access_token(self, *, user_id: str, kakao_id: int, email: str) -> str:
        return self._create_jwt(
            subject=user_id,
            token_type="access",
            expires_delta=timedelta(seconds=settings.access_token_expire_seconds),
            extra_claims={
                "kakao_id": kakao_id,
                "email": email,
            },
        )

    def create_refresh_token(self, *, user_id: str) -> str:
        return self._create_jwt(
            subject=user_id,
            token_type="refresh",
            expires_delta=timedelta(seconds=settings.refresh_token_expire_seconds),
            extra_claims={"jti": secrets.token_urlsafe(24)},
        )

    def _create_jwt(
        self,
        *,
        subject: str,
        token_type: str,
        expires_delta: timedelta,
        extra_claims: dict[str, Any],
    ) -> str:
        now = datetime.now(UTC)
        payload = {
            "iss": settings.jwt_issuer,
            "sub": subject,
            "type": token_type,
            "iat": int(now.timestamp()),
            "exp": int((now + expires_delta).timestamp()),
            **extra_claims,
        }
        header = {"alg": "HS256", "typ": "JWT"}

        header_part = self._base64url_json(header)
        payload_part = self._base64url_json(payload)
        signing_input = f"{header_part}.{payload_part}".encode()
        signature = hmac.new(
            settings.jwt_secret_key.encode(),
            signing_input,
            hashlib.sha256,
        ).digest()

        return f"{header_part}.{payload_part}.{self._base64url_bytes(signature)}"

    def _base64url_json(self, value: dict[str, Any]) -> str:
        return self._base64url_bytes(
            json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
        )

    def _base64url_bytes(self, value: bytes) -> str:
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


token_service = TokenService()
