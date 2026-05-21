from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth.tokens import TokenError, token_service

bearer_scheme = HTTPBearer()

class CurrentUser(BaseModel):
    id: str
    email: str | None = None
    kakao_id: int | None = None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    try:
        payload = token_service.verify_access_token(credentials.credentials)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return CurrentUser(
        id=str(payload["sub"]),
        email=payload.get("email"),
        kakao_id=payload.get("kakao_id"),
    )
