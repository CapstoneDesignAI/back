from app.db.base import supabase
from app.schemas.user import UserData

def build_user_profile_response(user_id: str) -> UserData:
    result = supabase.table("users") \
        .select("id, email, nickname, profile_img") \
        .eq("user_id", user_id) \
        .execute()
    
    return result.data
