from app.db.base import get_supabase
from app.schemas.places import PlaceCreateRequest

def create_or_get_place(payload: PlaceCreateRequest) -> tuple[str, bool]:
    supabase = get_supabase()
    place_id = payload.kakao_place_id

    existing_place = (
        supabase.table("places")
        .select("place_id")
        .eq("kakao_place_id", payload.kakao_place_id)
        .execute()
    )

    if existing_place.data:
        return str(existing_place.data[0]["place_id"]), False

    insert_payload = {
        "place_id": place_id,
        "kakao_place_id": payload.kakao_place_id,
        "name": payload.name,
        "lat": payload.latitude,
        "lng": payload.longitude,
        "address": payload.address,
        "category": payload.category,
        "description": _build_description(payload),
        "is_indoor": _infer_is_indoor(payload.category),
    }
    created_place = supabase.table("places").insert(insert_payload).execute()

    if created_place.data:
        return str(created_place.data[0]["place_id"]), True

    fetched_place = (
        supabase.table("places")
        .select("place_id")
        .eq("kakao_place_id", payload.kakao_place_id)
        .execute()
    )

    if fetched_place.data:
        return str(fetched_place.data[0]["place_id"]), True

    raise RuntimeError("장소 등록 후 place_id를 확인할 수 없습니다.")


def _build_description(payload: PlaceCreateRequest) -> str:
    category = payload.category.strip() if payload.category else "장소"
    return f"카카오맵에서 선택한 {category} 장소입니다."


def _infer_is_indoor(category: str) -> bool:
    indoor_keywords = (
        "동굴",
        "미술관",
        "박물관",
        "전시",
        "공연",
        "영화",
        "카페",
        "음식점",
        "식당",
        "시장",
        "쇼핑",
        "숙박",
    )
    return any(keyword in category for keyword in indoor_keywords)
