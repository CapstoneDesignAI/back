from typing import Any

from pydantic import BaseModel, Field


class KakaoLoginUrlResponse(BaseModel):
    authorization_url: str
    state: str


class KakaoTokenResponse(BaseModel):
    token_type: str
    access_token: str
    expires_in: int
    refresh_token: str | None = None
    refresh_token_expires_in: int | None = None
    scope: str | None = None


class KakaoUserProfile(BaseModel):
    id: int
    connected_at: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    kakao_account: dict[str, Any] = Field(default_factory=dict)


class KakaoCallbackResponse(BaseModel):
    provider: str
    state: str | None = None
    token: KakaoTokenResponse
    user: KakaoUserProfile
    
class RedirectResponse(BaseModel):
    url: str
