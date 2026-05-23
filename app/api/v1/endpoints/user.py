from fastapi import APIRouter, Depends

from app.core.jwt import get_current_user  
from app.schemas.user import UserData
from app.services.user.user_service import build_user_profile_response

router = APIRouter(prefix="/user")

@router.get("/profile", response_model=UserData)
async def get_user_profile(
    user_id: str = Depends(get_current_user),
) -> UserData:
    return await build_user_profile_response(user_id)
