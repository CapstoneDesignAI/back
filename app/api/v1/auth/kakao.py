from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from app.core.config import settings
from app.schemas.auth import KakaoLoginUrlResponse
from app.services.auth.kakao_oauth_service import KakaoAuthError, kakao_auth_service
from app.services.auth.supabase_users import SupabaseUserSyncError, supabase_user_service
from app.services.auth.tokens import token_service

router = APIRouter(prefix="/auth/kakao")

@router.get("", response_model=KakaoLoginUrlResponse, summary="카카오 로그인 URL 받아오기")
def get_kakao_login_url(
    state: str | None = Query(default=None),
    scope: str | None = Query(default=None),
) -> KakaoLoginUrlResponse:
    return kakao_auth_service.build_login_response(state=state, scope=scope)


@router.get("/callback", summary="카카오 로그인 콜백")
async def kakao_callback(
    code: str = Query(...),
):
    try:
        kakao_token = await kakao_auth_service.exchange_code_for_token(code=code)
        user = await kakao_auth_service.get_user_info(access_token=kakao_token.access_token)
        user_id = await supabase_user_service.save_kakao_user(user)
    except KakaoAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except SupabaseUserSyncError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    email = user.kakao_account.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Kakao account email is required to issue service tokens.",
        )

    access_token = token_service.create_access_token(
        user_id=user_id,
        kakao_id=user.id,
        email=str(email),
    )
    refresh_token = token_service.create_refresh_token(user_id=user_id)

    query = urlencode(
        {
            "accessToken": access_token,
            "refreshToken": refresh_token,
        }
    )
    return RedirectResponse(url=f"{settings.kakao_frontend_redirect_uri}?{query}")
