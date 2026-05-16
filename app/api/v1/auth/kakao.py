from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.auth import KakaoCallbackResponse, KakaoLoginUrlResponse,RedirectResponse
from app.services.auth.kakao import KakaoAuthError, kakao_auth_service

router = APIRouter(prefix="/auth/kakao")

@router.get("", response_model=KakaoLoginUrlResponse, summary="카카오 로그인 URL 받아오기")
def get_kakao_login_url(
    state: str | None = Query(default=None),
    scope: str | None = Query(default=None),
) -> KakaoLoginUrlResponse:
    return kakao_auth_service.build_login_response(state=state, scope=scope)


@router.get("/callback", response_model=KakaoCallbackResponse, summary="카카오 로그인 콜백")
async def kakao_callback(
    code: str = Query(...),
    state: str | None = Query(default=None),
) -> KakaoCallbackResponse:
    try:
        token = await kakao_auth_service.exchange_code_for_token(code=code)
        user = await kakao_auth_service.get_user_info(access_token=token.access_token)
    except KakaoAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    # TODO: 우리 서비스 유저 생성/조회
    # TODO: 우리 서비스 JWT 발급
    
    return RedirectResponse(
        url=f"capstoneai://login/success?accessToken={token.access_token}&refreshToken={token.refresh_token}"
        )
    
