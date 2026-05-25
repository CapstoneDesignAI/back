# app/services/routes/route_service.py
from app.db.base import get_supabase
from app.schemas.routes import RouteListItem, RouteDetailResponse

def get_routes(user_id: str) -> list[RouteListItem]:
    supabase = get_supabase()
    result = supabase.table("routes") \
        .select("id, title, created_at, route_places(count)") \
        .eq("user_id", user_id) \
        .execute()
    
    formatted_data = []
    for row in result.data:
        place_count = 0
        if row.get("route_places") and len(row["route_places"]) > 0:
            place_count = row["route_places"][0].get("count", 0)

        formatted_data.append({
            "route_id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "place_count": place_count
        })
        
    return formatted_data

def get_route_detail(route_id: str) -> RouteDetailResponse:
    supabase = get_supabase()
    result = supabase.table("routes") \
        .select("id, title, created_at, route_places(visit_order, place_id, description, tags, places(name, address, lat, lng, image_url, category))") \
        .eq("route_id", route_id) \
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
