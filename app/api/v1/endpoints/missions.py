from fastapi import APIRouter, Depends, Query
from app.schemas.missions import MissionListItem
from app.services.mission_service import get_missions_by_region
from app.core.jwt import get_current_user

router = APIRouter(prefix="/missions", tags=["Missions"])

@router.get("", response_model=list[MissionListItem], summary="특정 지역 미션 목록 조회")
def read_missions(
    region_id: str = Query(..., description="조회할 지역의 고유 ID"),
    user_id: str = "5fd0d467-03cb-4364-b8da-bb1d94d32f35"
):
    result = get_missions_by_region(user_id, region_id)
    return result