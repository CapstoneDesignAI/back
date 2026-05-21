from fastapi import APIRouter, HTTPException
from app.schemas.user import UserData
from app.services.user.user_service import build_user_profile_response

router = APIRouter(prefix="/user")

@router.get("/profile", response_model=UserData)
def get_user_profile(current_user=get_current_user):
    return build_user_profile_response(current_user.id)
