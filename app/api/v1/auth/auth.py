from fastapi import APIRouter

from app.schemas.auth import LogoutResponse

router = APIRouter(prefix="/auth")


@router.post("/logout", response_model=LogoutResponse, summary="로그아웃")
def logout() -> LogoutResponse:
    return LogoutResponse(message="로그아웃 되었습니다.")
