from fastapi import APIRouter, Depends
from app.schemas.emblems import EmblemItem
from app.services.emblem_service import get_user_emblems
from app.core.jwt import get_current_user

router = APIRouter(prefix="/emblems", tags=["emblems"])

@router.get("", response_model=list[EmblemItem], summary="내 엠블럼 보관함 조회")
def read_emblems(
    user_id: str = "5fd0d467-03cb-4364-b8da-bb1d94d32f35"
):
    result = get_user_emblems(user_id)
    return result