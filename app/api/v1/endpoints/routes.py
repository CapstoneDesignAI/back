# back\app\api\v1\endpoints\routes.py
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.routes import RouteListItem, RouteDetailResponse
from app.services.route_service import get_routes, get_route_detail, create_recommended_route
from app.core.jwt import get_current_user 
from app.schemas.recommendations import AIRecommendationResponse

router = APIRouter(prefix="/routes")

@router.get("", response_model=list[RouteListItem])
def read_routes(user_id: str = Depends(get_current_user)):
    return get_routes(user_id)

@router.get("/{route_id}", response_model=RouteDetailResponse)
def read_route_detail(route_id: str):
    result = get_route_detail(route_id)
    if not result:
        raise HTTPException(status_code=404, detail="동선을 찾을 수 없습니다.")
    return result

@router.post("", status_code=status.HTTP_201_CREATED, summary="추천받은 동선 저장하기")
def save_recommended_route(
    request_data: AIRecommendationResponse,
    user_id: str = Depends(get_current_user)
):
    success = create_recommended_route(user_id, request_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="동선을 DB에 저장하는 데 실패했습니다.")

    return {"message": "동선이 성공적으로 저장되었습니다."}