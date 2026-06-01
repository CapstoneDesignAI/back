from app.db.base import get_supabase
from app.schemas.emblems import EmblemItem

def get_user_emblems(user_id: str) -> list[EmblemItem]:
    supabase = get_supabase()
    
    all_emblems_res = supabase.table("emblems") \
        .select("*") \
        .order("unlock_stamp_threshold") \
        .execute()
        
    if not all_emblems_res.data:
        return []
        
    user_emblems_res = supabase.table("user_emblems") \
        .select("emblem_id, acquired_at") \
        .eq("user_id", user_id) \
        .execute()
        
    acquired_dict = {
        row["emblem_id"]: row["acquired_at"] 
        for row in user_emblems_res.data
    }

    formatted_data = []
    for emblem in all_emblems_res.data:
        emblem_id = emblem["id"]
        is_acquired = emblem_id in acquired_dict
        acquired_time = acquired_dict.get(emblem_id) if is_acquired else None
        
        formatted_data.append(
            EmblemItem(
                emblem_id=emblem_id,
                name=emblem["name"],
                description=emblem["description"],
                image_url=emblem["image_url"],
                unlock_stamp_threshold=emblem["unlock_stamp_threshold"],
                is_acquired=is_acquired,
                acquired_at=acquired_time
            )
        )
        
    return formatted_data