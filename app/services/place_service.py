from app.db.base import get_supabase
from app.schemas.places import PlaceCreateRequest

def create_or_get_place(payload: PlaceCreateRequest) -> tuple[str, bool]:
    supabase = get_supabase()

    existing_place = (
        supabase.table("places")
        .select("id")
        .eq("kakao_place_id", payload.kakao_place_id)
        .execute()
    )

    if existing_place.data:
        return str(existing_place.data[0]["id"]), False

    insert_payload = {
        "kakao_place_id": payload.kakao_place_id,
        "name": payload.name,
        "lat": payload.latitude,
        "lng": payload.longitude,
        "address": payload.address,
        "category": payload.category,
    }
    created_place = supabase.table("places").insert(insert_payload).execute()

    if created_place.data:
        return str(created_place.data[0]["id"]), True

    fetched_place = (
        supabase.table("places")
        .select("id")
        .eq("kakao_place_id", payload.kakao_place_id)
        .execute()
    )

    if fetched_place.data:
        return str(fetched_place.data[0]["id"]), True

    raise RuntimeError("장소 등록 후 place_id를 확인할 수 없습니다.")
