from fastapi import APIRouter, Depends
from app.schemas.stamps import StampBoardResponse
from app.services.stamp_service import get_user_stamp_boards
from app.core.jwt import get_current_user

router = APIRouter(prefix="/stamps", tags=["stamps"])

@router.get("", response_model=list[StampBoardResponse], summary="내 전체 지역 스탬프 쿠폰 조회")
def read_stamp_boards(
    user_id: str = Depends(get_current_user)
):
    result = get_user_stamp_boards(user_id)
    return result
