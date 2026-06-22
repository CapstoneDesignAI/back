from app.db.base import get_supabase
from app.schemas.stamps import StampBoardResponse


def get_user_stamp_boards(user_id: str) -> list[StampBoardResponse]:
    supabase = get_supabase()

    wallet_res = supabase.table("user_region_stamps") \
        .select("region_id, collected_stamps, updated_at") \
        .eq("user_id", user_id) \
        .order("updated_at", desc=True) \
        .execute()

    wallets = wallet_res.data or []
    if not wallets:
        return []

    region_ids = [wallet["region_id"] for wallet in wallets if wallet.get("region_id")]
    regions = []
    if region_ids:
        regions_res = supabase.table("regions") \
            .select("id, name") \
            .in_("id", region_ids) \
            .execute()
        regions = regions_res.data or []

    region_names = {
        region["id"]: region.get("name") or "알 수 없는 지역"
        for region in regions
    }

    return [
        StampBoardResponse(
            region_id=wallet["region_id"],
            region_name=region_names.get(wallet["region_id"], "알 수 없는 지역"),
            collected_stamps=wallet.get("collected_stamps") or 0,
            total_stamps=10,
            next_reward_text=_build_next_reward_text(wallet.get("collected_stamps") or 0),
        )
        for wallet in wallets
    ]


def _build_next_reward_text(collected: int) -> str:
    if collected < 1:
        return "스탬프 1개를 모으면 첫 엠블럼을 드려요!"
    elif collected < 5:
        return f"앞으로 {5 - collected}개 더 모으면 다음 엠블럼을 드려요!"
    elif collected < 10:
        return f"앞으로 {10 - collected}개 더 모으면 최종 엠블럼을 드려요!"
    return "축하합니다! 이 지역의 모든 보상을 획득하셨습니다! 🎉"
