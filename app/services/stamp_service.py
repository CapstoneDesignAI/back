from app.db.base import get_supabase
from app.schemas.stamps import StampBoardResponse

def get_user_stamp_board(user_id: str, region_id: str) -> StampBoardResponse:
    supabase = get_supabase()
    
    region_res = supabase.table("regions") \
        .select("name") \
        .eq("id", region_id) \
        .single() \
        .execute()
        
    region_name = region_res.data.get("name") if region_res.data else "알 수 없는 지역"
    
    wallet_res = supabase.table("user_region_stamps") \
        .select("collected_stamps") \
        .eq("user_id", user_id) \
        .eq("region_id", region_id) \
        .execute()
    
    collected = 0
    if wallet_res.data:
        collected = wallet_res.data[0]["collected_stamps"]
        
    if collected < 1:
        next_text = "스탬프 1개를 모으면 첫 엠블럼을 드려요!"
    elif collected < 5:
        next_text = f"앞으로 {5 - collected}개 더 모으면 다음 엠블럼을 드려요!"
    elif collected < 10:
        next_text = f"앞으로 {10 - collected}개 더 모으면 최종 엠블럼을 드려요!"
    else:
        next_text = "축하합니다! 이 지역의 모든 보상을 획득하셨습니다! 🎉"
        
    return StampBoardResponse(
        region_id=region_id,
        region_name=region_name,
        collected_stamps=collected,
        total_stamps=10,
        next_reward_text=next_text
    )