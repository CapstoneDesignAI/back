from app.db.base import get_supabase
from app.schemas.routes import RouteListItem, RouteDetailResponse
from app.schemas.recommendations import RecommendationSavePayload
from app.services.recommendations import get_recommendation_detail

def get_routes(user_id: str) -> list[RouteListItem]:
    supabase = get_supabase()
    result = supabase.table("routes") \
        .select("id, title, created_at, route_places(visit_order, places(image_url))") \
        .eq("user_id", user_id) \
        .execute()
    
    formatted_data = []
    for row in result.data:
        route_places = row.get("route_places") or []
        place_count = len(route_places)
        
        # 첫 번째 장소의 이미지를 썸네일로 사용
        thumbnail_url = None
        if route_places:
            sorted_places = sorted(route_places, key=lambda x: x.get("visit_order", 999))
            for rp in sorted_places:
                place_info = rp.get("places")
                if place_info and isinstance(place_info, dict) and place_info.get("image_url"):
                    thumbnail_url = place_info.get("image_url")
                    break

        formatted_data.append({
            "route_id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "place_count": place_count,
            "image_url": thumbnail_url
        })
        
    return formatted_data

def get_route_detail(route_id: str) -> RouteDetailResponse:
    supabase = get_supabase()
    result = supabase.table("routes") \
        .select("id, title, created_at, route_places(visit_order, place_id, description, tags, places(name, address, lat, lng, image_url, category))") \
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
        "description": data.get("description") or "AI가 생성한 맞춤 여행 코스입니다.",
        "tags": data.get("tags") or ["추천", "힐링"],
        "places": formatted_places
    }

def create_recommended_route(user_id: str, route_data: RecommendationSavePayload) -> str | None:
    supabase = get_supabase()
    
    try:
        route_insert_result = supabase.table("routes").insert({
            "user_id": user_id,
            "title": route_data.title,
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
                "tags": place.tags
            })
            
            # 동선 저장 시 장소 테이블의 이미지 URL 업데이트 (존재하고 유효한 경우)
            if place.image_url:
                try:
                    supabase.table("places").update({"image_url": place.image_url}).eq("id", place.place_id).execute()
                except Exception as update_err:
                    print(f"⚠️ 장소 이미지 업데이트 실패 ({place.place_id}): {update_err}")
            
        if places_to_insert:
            supabase.table("route_places").insert(places_to_insert).execute()
            
        return str(new_route_id)
        
    except Exception as e:
        print(f"❌ DB 저장 중 에러 발생: {e}")
        return None
    
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
