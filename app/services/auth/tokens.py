import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings

class TokenError(Exception):
    """JWT token validation fails."""

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

    def verify_access_token(self, token: str) -> dict[str, Any]:
        payload = self._verify_jwt(token)
        if payload.get("type") != "access":
            raise TokenError("Token type must be access.")
        if not payload.get("sub"):
            raise TokenError("Token subject is missing.")
        return payload

    def _verify_jwt(self, token: str) -> dict[str, Any]:
        try:
            header_part, payload_part, signature_part = token.split(".")
        except ValueError as exc:
            raise TokenError("Invalid token format.") from exc

        try:
            header = self._base64url_json_decode(header_part)
            payload = self._base64url_json_decode(payload_part)
            signature = self._base64url_decode(signature_part)
        except (ValueError, json.JSONDecodeError) as exc:
            raise TokenError("Invalid token encoding.") from exc

        if header.get("alg") != "HS256" or header.get("typ") != "JWT":
            raise TokenError("Unsupported token header.")

        signing_input = f"{header_part}.{payload_part}".encode()
        expected_signature = hmac.new(
            settings.jwt_secret_key.encode(),
            signing_input,
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(signature, expected_signature):
            raise TokenError("Invalid token signature.")

        if payload.get("iss") != settings.jwt_issuer:
            raise TokenError("Invalid token issuer.")

        exp = payload.get("exp")
        if not isinstance(exp, int):
            raise TokenError("Token expiration is missing.")
        if exp <= int(datetime.now(UTC).timestamp()):
            raise TokenError("Token has expired.")

        return payload

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

    def _base64url_json_decode(self, value: str) -> dict[str, Any]:
        decoded = self._base64url_decode(value)
        parsed = json.loads(decoded)
        if not isinstance(parsed, dict):
            raise ValueError("JWT part must decode to an object.")
        return parsed

    def _base64url_decode(self, value: str) -> bytes:
        padded_value = value + "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(padded_value)


token_service = TokenService()
