from app.db.base import get_supabase
from app.schemas.missions import MissionListItem

def get_missions_by_region(user_id: str, region_id: str) -> list[MissionListItem]:
    supabase = get_supabase()

    missions_res = supabase.table("missions") \
        .select("id, title, reward_stamp_count, difficulty") \
        .eq("region_id", region_id) \
        .execute()
        
    if not missions_res.data:
        return []

    completed_res = supabase.table("user_missions") \
        .select("mission_id") \
        .eq("user_id", user_id) \
        .eq("is_completed", True) \
        .execute()
        
    completed_mission_ids = {row["mission_id"] for row in completed_res.data}

    formatted_data = []
    for mission in missions_res.data:
        is_done = mission["id"] in completed_mission_ids 
        
        formatted_data.append(
            MissionListItem(
                mission_id=mission["id"],
                title=mission["title"],
                stamp_count=mission["reward_stamp_count"],
                difficulty=mission["difficulty"],
                is_completed=is_done
            )
        )
        
    return formatted_data