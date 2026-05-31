from fastapi import APIRouter, Depends, Query, BackgroundTasks, status
from app.schemas.missions import MissionListItem, MissionDetailResponse, MissionVerifyRequest, MissionVerifyResponse
from app.services.mission_service import get_missions_by_region, get_mission_detail, request_mission_verification, auto_approve_mission_task
from app.core.jwt import get_current_user

router = APIRouter(prefix="/missions", tags=["Missions"])

@router.get("", response_model=list[MissionListItem], summary="특정 지역 미션 목록 조회")
def read_missions(
    region_id: str = Query(..., description="조회할 지역의 고유 ID"),
    user_id: str = "5fd0d467-03cb-4364-b8da-bb1d94d32f35" #Depends(get_current_user)
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

@router.post(
    "/{mission_id}/verify", 
    response_model=MissionVerifyResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="미션 인증 요청 (사진 및 GPS)"
)
def verify_mission(
    mission_id: str,
    payload: MissionVerifyRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "5fd0d467-03cb-4364-b8da-bb1d94d32f35" #Depends(get_current_user)
):
    result = request_mission_verification(user_id, mission_id, payload)
    
    background_tasks.add_task(
        auto_approve_mission_task, 
        user_id=user_id, 
        mission_id=mission_id, 
        user_mission_id=result.user_mission_id
    )
    
    return result