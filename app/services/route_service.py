from app.db.base import get_supabase
from app.schemas.routes import RouteListItem, RouteDetailResponse
from app.schemas.recommendations import RecommendationSavePayload
from app.services.recommendations import get_recommendation_detail


def get_routes(user_id: str) -> list[RouteListItem]:
    supabase = get_supabase()
    result = supabase.table("routes") \
        .select("id, title, created_at, image_url, route_places(visit_order)") \
        .eq("user_id", user_id) \
        .execute()
    
    formatted_data = []
    for row in result.data:
        route_places = row.get("route_places") or []
        place_count = len(route_places)
        
        formatted_data.append({
            "route_id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "place_count": place_count,
            "image_url": row.get("image_url")
        })
        
    return formatted_data

def get_route_detail(route_id: str) -> RouteDetailResponse:
    supabase = get_supabase()
    result = supabase.table("routes") \
        .select("id, title, created_at, image_url, route_places(visit_order, place_id, description, tags, places(name, address, lat, lng, image_url, category))") \
        .eq("id", route_id) \
        .single() \
        .execute()
    
    data = result.data
    if not data:
        return None
        
    formatted_places = []
    for rp in data.get("route_places", []):
        place_info = rp.get("places", {})
        formatted_places.append({
            "visit_order": rp["visit_order"],
            "place_id": rp["place_id"],
            "name": place_info.get("name"),
            "address": place_info.get("address"),
            "lat": place_info.get("lat"),
            "lng": place_info.get("lng"),
            "image_url": place_info.get("image_url") or "",
            "description": rp.get("description") or "AI가 추천하는 멋진 장소입니다.",
            "tags": rp.get("tags") or [],
            "category": place_info.get("category") or "기타"
        })
        
    return {
        "route_id": data["id"],
        "title": data["title"],
        "created_at": data["created_at"],
        "image_url": data.get("image_url"),
        "description": data.get("description") or "AI가 생성한 맞춤 여행 코스입니다.",
        "tags": data.get("tags") or ["추천", "힐링"],
        "places": formatted_places
    }

def create_recommended_route(user_id: str, route_data: RecommendationSavePayload) -> str | None:
    supabase = get_supabase()
    
    try:
        place_payloads = [_to_place_upsert_payload(place) for place in route_data.places]
        if place_payloads:
            supabase.table("places").upsert(place_payloads, on_conflict="place_id").execute()

        route_insert_result = supabase.table("routes").insert({
            "user_id": user_id,
            "title": route_data.title,
            "image_url": route_data.image_url,
        }).execute()
        
        inserted_route = route_insert_result.data[0]
        new_route_id = inserted_route["id"]
        
        places_to_insert = []
        for place in route_data.places:
            places_to_insert.append({
                "route_id": new_route_id,
                "place_id": place.place_id,
                "visit_order": place.visit_order,
                "description": place.description,
                "tags": place.tags,
            })
            
        if places_to_insert:
            supabase.table("route_places").insert(places_to_insert).execute()
            
        return str(new_route_id)
        
    except Exception as e:
        print(f"❌ DB 저장 중 에러 발생: {e}")
        return None


def _to_place_upsert_payload(place) -> dict:
    return {
        "place_id": place.place_id,
        "name": place.name,
        "address": place.address,
        "lat": place.lat,
        "lng": place.lng,
        "category": place.category,
        "description": place.description,
        "image_url": place.image_url or None,
        "is_indoor": _infer_is_indoor(place.category),
    }


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
        "맛집",
        "로컬시장",
    )
    return any(keyword in category for keyword in indoor_keywords)
    
def create_recommended_route_from_route_id(user_id: str, route_id: str) -> str | None:
    recommendation = get_recommendation_detail(route_id)
    if recommendation is None:
        return None

    return create_recommended_route(
        user_id=user_id,
        route_data=recommendation.legacy_route_payload,
    )


def delete_route(user_id: str, route_id: str) -> bool:
    supabase = get_supabase()
    try:
        result = supabase.table("routes") \
            .delete() \
            .eq("id", route_id) \
            .eq("user_id", user_id) \
            .execute()
            
        return len(result.data) > 0
    except Exception as e:
        print(f"❌ 동선 삭제 중 에러 발생: {e}")
        return False
