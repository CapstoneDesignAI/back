from app.db.base import get_supabase
from app.schemas.missions import MissionListItem, MissionDetailResponse
from fastapi import HTTPException

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

def get_mission_detail(user_id: str, mission_id: str) -> MissionDetailResponse:
    supabase = get_supabase()
    
    mission_res = supabase.table("missions") \
        .select("*, places(name, lat, lng)") \
        .eq("id", mission_id) \
        .single() \
        .execute()
        
    if not mission_res.data:
        raise HTTPException(status_code=404, detail="해당 미션을 찾을 수 없습니다.")
        
    mission_data = mission_res.data
    place_data = mission_data.get("places", {}) 
    
    completed_res = supabase.table("user_missions") \
        .select("id") \
        .eq("user_id", user_id) \
        .eq("mission_id", mission_id) \
        .eq("is_completed", True) \
        .execute()
        
    is_done = len(completed_res.data) > 0

    return MissionDetailResponse(
        mission_id=mission_data["id"],
        region_id=mission_data["region_id"],
        title=mission_data["title"],
        description=mission_data.get("description"),
        reward_stamp_count=mission_data["reward_stamp_count"],
        difficulty=mission_data["difficulty"],
        distance_text=mission_data["distance_text"],
        place_name=place_data.get("name") or "알 수 없는 장소",
        lat=place_data.get("lat") or 0.0,
        lng=place_data.get("lng") or 0.0,
        is_completed=is_done
    )