import httpx
from fastapi import HTTPException, status

from app.db.supabase import (
    SupabaseConfigError,
    SupabaseRequestError,
    supabase_client,
)
from app.schemas.user import UserData

async def build_user_profile_response(user_id: str) -> UserData:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                supabase_client.rest_url("/users"),
                headers=supabase_client.headers(),
                params={
                    "select": "id,email, nickname, profile_img",
                    "id": f"eq.{user_id}",
                    "limit": "1",
                },
            )
    except SupabaseConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    try:
        supabase_client.raise_for_error(response, "Failed to fetch user profile")
    except SupabaseRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

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
