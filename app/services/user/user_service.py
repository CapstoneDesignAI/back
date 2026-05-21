import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.user import UserData

def _supabase_headers() -> dict[str, str]: 
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase settings are not configured.",
        )

    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
    }

async def build_user_profile_response(user_id: str) -> UserData:
    if not settings.supabase_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_URL is not configured.",
        )

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{settings.supabase_url.rstrip('/')}/rest/v1/users",
            headers=_supabase_headers(),
            params={
                "select": "id,email, nickname, profile_img",
                "id": f"eq.{user_id}",
                "limit": "1",
            },
        )

    if response.is_error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch user profile: {response.text}",
        )

    users = response.json()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    user = users[0]
    return UserData(
        id=str(user["id"]),
        nickName=str(user["nickname"]),
        email=str(user["email"]),
        profile_img=user.get("profile_img"),
    )
