from fastapi import APIRouter, HTTPException, status

from app.schemas.places import PlaceCreateRequest, PlaceCreateResponse
from app.services import place_service

router = APIRouter(prefix="/places")

@router.post(
    "",
    response_model=PlaceCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="신규 장소 등록 또는 기존 장소 조회",
    
)
def create_place(payload: PlaceCreateRequest) -> PlaceCreateResponse:
    try:
        place_id, is_newly_created = place_service.create_or_get_place(payload)
    except Exception as exc:
        print(f"장소 등록/조회 중 에러 발생: {exc}")
        raise HTTPException(
            status_code=500,
            detail="장소 등록/조회에 실패했습니다.",
        ) from exc

    return PlaceCreateResponse(
        message="장소가 성공적으로 등록/조회되었습니다.",
        place_id=place_id,
        is_newly_created=is_newly_created,
    )
