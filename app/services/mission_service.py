import asyncio
from uuid import UUID
from fastapi import HTTPException
from app.db.base import get_supabase
from app.schemas.missions import MissionListItem, MissionDetailResponse, MissionVerifyRequest, MissionVerifyResponse
from app.core.geo import calculate_distance_in_meters

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
        .eq("status", "APPROVED") \
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
    resolved_mission_id = _resolve_mission_id(supabase, mission_id)
    
    mission_res = supabase.table("missions") \
        .select("*, places(name, lat, lng)") \
        .eq("id", resolved_mission_id) \
        .single() \
        .execute()
        
    if not mission_res.data:
        raise HTTPException(status_code=404, detail="해당 미션을 찾을 수 없습니다.")
        
    mission_data = mission_res.data
    place_data = mission_data.get("places", {}) 
    
    completed_res = supabase.table("user_missions") \
        .select("id") \
        .eq("user_id", user_id) \
        .eq("mission_id", resolved_mission_id) \
        .eq("status", "APPROVED") \
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

def request_mission_verification(user_id: str, mission_id: str, payload: MissionVerifyRequest) -> MissionVerifyResponse:
    supabase = get_supabase()
    resolved_mission_id = _resolve_mission_id(supabase, mission_id)
    
    mission_res = supabase.table("missions").select("*, places(lat, lng)").eq("id", resolved_mission_id).single().execute()
    if not mission_res.data:
        raise HTTPException(status_code=404, detail="해당 미션을 찾을 수 없습니다.")
        
    place_data = mission_res.data.get("places", {})
    target_lat = place_data.get("lat")
    target_lng = place_data.get("lng")
    
    if target_lat and target_lng:
        distance = calculate_distance_in_meters(payload.latitude, payload.longitude, target_lat, target_lng)
        if distance > 100.0:
            raise HTTPException(status_code=400, detail=f"인증 장소에서 너무 멉니다. (거리: 약 {int(distance)}m)")

    existing = supabase.table("user_missions").select("id, status").eq("user_id", user_id).eq("mission_id", resolved_mission_id).execute()
    
    if existing.data:
        current_status = existing.data[0]["status"]
        
        if current_status in ["PENDING", "APPROVED"]:
            raise HTTPException(status_code=409, detail="이미 인증 요청되었거나 완료된 미션입니다.")
            
        existing_id = existing.data[0]["id"]
        supabase.table("user_missions").update({
            "image_url": payload.image_url,
            "status": "PENDING"
        }).eq("id", existing_id).execute()
        
        return MissionVerifyResponse(
            message="재인증 요청이 성공적으로 접수되었습니다. (1.5초 뒤 자동 승인)",
            user_mission_id=existing_id,
            status="PENDING"
        )

    insert_res = supabase.table("user_missions").insert({
        "user_id": user_id,
        "mission_id": resolved_mission_id,
        "image_url": payload.image_url,
        "status": "PENDING" 
    }).execute()
    
    return MissionVerifyResponse(
        message="인증 요청이 성공적으로 접수되었습니다. (1.5초 뒤 자동 승인)",
        user_mission_id=insert_res.data[0]["id"],
        status="PENDING"
    )

async def auto_approve_mission_task(user_id: str, mission_id: str, user_mission_id: str):
    await asyncio.sleep(1.5)
    print(f"1.5초 경과 유저 {user_id}의 미션({mission_id})이 자동 승인됩니다.")
    
    supabase = get_supabase()
    
    try:
        resolved_mission_id = _resolve_mission_id(supabase, mission_id)
        supabase.table("user_missions").update({"status": "APPROVED"}).eq("id", user_mission_id).execute()
        
        mission_res = supabase.table("missions") \
            .select("region_id, reward_stamp_count") \
            .eq("id", resolved_mission_id).single().execute()
            
        region_id = mission_res.data["region_id"]
        reward_count = mission_res.data["reward_stamp_count"]
        
        wallet_res = supabase.table("user_region_stamps") \
            .select("id, collected_stamps") \
            .eq("user_id", user_id).eq("region_id", region_id).execute()
            
        if wallet_res.data:
            current_stamps = wallet_res.data[0]["collected_stamps"]
            new_stamps = current_stamps + reward_count
            supabase.table("user_region_stamps").update({"collected_stamps": new_stamps}).eq("id", wallet_res.data[0]["id"]).execute()
        else:
            current_stamps = 0
            new_stamps = reward_count
            supabase.table("user_region_stamps").insert({
                "user_id": user_id, 
                "region_id": region_id, 
                "collected_stamps": new_stamps
            }).execute()
            
        print(f"스탬프 지급 완료! 현재 누적 스탬프: {new_stamps}개 (이전: {current_stamps}개)")
        
        emblems_res = supabase.table("emblems") \
            .select("id, name, unlock_stamp_threshold") \
            .eq("region_id", region_id) \
            .gt("unlock_stamp_threshold", current_stamps) \
            .lte("unlock_stamp_threshold", new_stamps) \
            .execute()
            
        if emblems_res.data:
            new_user_emblems = [{"user_id": user_id, "emblem_id": e["id"]} for e in emblems_res.data]
            supabase.table("user_emblems").insert(new_user_emblems).execute()
            
            earned_names = [e["name"] for e in emblems_res.data]
            print(f"🎉 엠블럼 획득! 지급된 엠블럼: {earned_names}")
        
    except Exception as e:
        print(f"자동 승인 중 문제 발생: {e}")


def _resolve_mission_id(supabase, mission_identifier: str) -> str:
    if _is_uuid(mission_identifier):
        return mission_identifier

    try:
        result = (
            supabase.table("missions")
            .select("id")
            .eq("slug", mission_identifier)
            .single()
            .execute()
        )
    except Exception as error:
        if _is_missing_column_error(error, "slug", "missions") or _is_not_found_error(error):
            raise HTTPException(status_code=404, detail="해당 미션을 찾을 수 없습니다.") from error
        raise

    if not result.data:
        raise HTTPException(status_code=404, detail="해당 미션을 찾을 수 없습니다.")

    return result.data["id"]


def _is_uuid(value: str) -> bool:
    try:
        UUID(value)
    except ValueError:
        return False
    return True


def _is_missing_column_error(error: Exception, column: str, table: str) -> bool:
    message = str(error)
    return (
        f"column {table}.{column} does not exist" in message
        or (
            "PGRST204" in message
            and f"'{column}' column" in message
            and f"'{table}'" in message
        )
    )


def _is_not_found_error(error: Exception) -> bool:
    message = str(error)
    return "PGRST116" in message or "Cannot coerce the result to a single JSON object" in message
