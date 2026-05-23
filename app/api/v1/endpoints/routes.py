from fastapi import APIRouter, HTTPException, Depends
from app.schemas.routes import RouteListItem, RouteDetailResponse
from app.services.route_service import get_routes, get_route_detail
from app.core.jwt import get_current_user  

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