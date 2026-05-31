from fastapi import APIRouter, Depends, Query
from app.schemas.missions import MissionListItem, MissionDetailResponse
from app.services.mission_service import get_missions_by_region, get_mission_detail
from app.core.jwt import get_current_user

router = APIRouter(prefix="/missions", tags=["Missions"])

@router.get("", response_model=list[MissionListItem], summary="특정 지역 미션 목록 조회")
def read_missions(
    region_id: str = Query(..., description="조회할 지역의 고유 ID"),
    user_id: str = "5fd0d467-03cb-4364-b8da-bb1d94d32f35"
):
    result = get_missions_by_region(user_id, region_id)
    return result

@router.get("/{mission_id}", response_model=MissionDetailResponse, summary="미션 상세 정보 조회")
def read_mission_detail(
    mission_id: str,
    user_id: str = "5fd0d467-03cb-4364-b8da-bb1d94d32f35" #Depends(get_current_user)
):
    result = get_mission_detail(user_id, mission_id)
    return result