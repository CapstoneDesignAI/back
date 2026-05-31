from fastapi import APIRouter, Depends, Query
from app.schemas.stamps import StampBoardResponse
from app.services.stamp_service import get_user_stamp_board
from app.core.jwt import get_current_user

router = APIRouter(prefix="/stamps", tags=["stamps"])

@router.get("", response_model=StampBoardResponse, summary="내 지역별 스탬프 쿠폰 조회")
def read_stamp_board(
    region_id: str = Query(..., description="조회할 지역 ID"),
    user_id: str = Depends(get_current_user)
):
    result = get_user_stamp_board(user_id, region_id)
    return result