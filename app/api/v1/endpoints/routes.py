from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.routes import (
    RouteCreateResponse,
    RouteDetailResponse,
    RouteListItem,
    RouteTransportationResponse,
    RouteSaveFromRecommendationRequest,
    RouteSaveFromRecommendationResponse,
)
from app.services.odsay_service import get_transportation_segments
from app.core.jwt import get_current_user 

from app.schemas.recommendations import RecommendationSavePayload
from app.services.route_service import (
    create_recommended_route,
    create_recommended_route_from_route_id,
    delete_route,
    get_route_detail,
    get_routes,
)

router = APIRouter(prefix="/routes")


@router.get("", response_model=list[RouteListItem], summary="동선 조회하기")
def read_routes(user_id: str = Depends(get_current_user)):
    return get_routes(user_id)


@router.get("/{route_id}", response_model=RouteDetailResponse, summary="동선 세부사항 조회하기")
def read_route_detail(route_id: str):
    result = get_route_detail(route_id)
    if not result:
        raise HTTPException(status_code=404, detail="동선을 찾을 수 없습니다.")
    return result


@router.get(
    "/{route_id}/transportation",
    response_model=RouteTransportationResponse,
    summary="동선 장소별 교통 및 이동 안내",
)
def read_route_transportation(route_id: str):
    result = get_transportation_segments(route_id)
    if result is None:
        raise HTTPException(status_code=404, detail="동선을 찾을 수 없습니다.")
    return result


@router.post(
    "",
    response_model=RouteCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="추천받은 동선 저장하기",
)
def save_recommended_route(
    request_data: RecommendationSavePayload,
    user_id: str = Depends(get_current_user),
) -> RouteCreateResponse:
    route_id = create_recommended_route(user_id, request_data)

    if not route_id:
        raise HTTPException(status_code=500, detail="동선을 DB에 저장하지 못했습니다.")

    return RouteCreateResponse(
        message="동선이 성공적으로 저장되었습니다.",
        route_id=route_id,
    )


@router.post(
    "/from-recommendation",
    response_model=RouteSaveFromRecommendationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="route_id로 추천 동선 저장하기",
)
def save_recommended_route_from_route_id(
    request_data: RouteSaveFromRecommendationRequest,
    user_id: str = Depends(get_current_user),
) -> RouteSaveFromRecommendationResponse:
    saved_route_id = create_recommended_route_from_route_id(
        user_id=user_id,
        route_id=request_data.route_id,
    )

    if not saved_route_id:
        raise HTTPException(
            status_code=404,
            detail="추천 동선을 찾을 수 없거나 저장에 실패했습니다.",
        )

    return RouteSaveFromRecommendationResponse(
        message="동선이 성공적으로 저장되었습니다.",
        route_id=saved_route_id,
        saved_route_id=saved_route_id,
        source_route_id=request_data.route_id,
        source_detail_api_path=f"/api/v1/ai-recommendations/{request_data.route_id}",
        saved_detail_api_path=f"/api/v1/routes/{saved_route_id}",
        is_saved=True,
    )


@router.delete("/{route_id}", summary="저장한 동선 삭제")
def remove_route(
    route_id: str,
    user_id: str = Depends(get_current_user),
):
    success = delete_route(user_id, route_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="삭제할 권한이 없거나 존재하지 않는 동선입니다.",
        )

    return {"message": "동선이 성공적으로 삭제되었습니다."}
