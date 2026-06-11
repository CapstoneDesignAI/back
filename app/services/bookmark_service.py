from app.db.base import get_supabase
from app.schemas.bookmarks import BookmarkAddRequest, BookmarkAddResponse, BookmarkedPlaceResponse
from app.services import place_service

def add_bookmark(user_id: str, payload: BookmarkAddRequest) -> BookmarkAddResponse | None:
    supabase = get_supabase()
    
    try:
        target_folder_id = payload.folder_id
        
        if not target_folder_id:
            folder_res = supabase.table("folders") \
                .select("id") \
                .eq("user_id", user_id) \
                .eq("is_default", True) \
                .execute()
                
            if folder_res.data:
                target_folder_id = folder_res.data[0]["id"]
            else:
                return None

        place_id = payload.place_id
        is_newly_created_place = False

        if payload.place:
            place_id, is_newly_created_place = place_service.create_or_get_place(payload.place)

        if not place_id:
            return None

        bookmark_res = supabase.table("bookmarks").insert({
            "user_id": user_id,
            "folder_id": target_folder_id,
            "place_id": place_id
        }).execute()

        bookmark_id = None
        if bookmark_res.data:
            bookmark_id = str(bookmark_res.data[0].get("id"))

        return BookmarkAddResponse(
            message="장소가 즐겨찾기에 성공적으로 추가되었습니다.",
            bookmark_id=bookmark_id,
            place_id=place_id,
            is_newly_created_place=is_newly_created_place,
        )
    except Exception as e:
        print(f"❌ 즐겨찾기 추가 중 에러 발생: {e}")
        return None


def get_bookmarked_places(user_id: str, folder_id: str | None = None) -> list[BookmarkedPlaceResponse]:
    supabase = get_supabase()

    query = supabase.table("bookmarks").select("id, folder_id, place_id, places(name, address, image_url, category)").eq("user_id", user_id)
    
    if folder_id:
        query = query.eq("folder_id", folder_id)
        
    result = query.execute()
    
    formatted_data = []
    for row in result.data:
        place_info = row.get("places") or {}
        formatted_data.append({
            "bookmark_id": str(row["id"]),
            "folder_id": row["folder_id"],
            "place_id": row["place_id"],
            "name": place_info.get("name") or "이름 없음",
            "address": place_info.get("address") or "주소 없음",
            "image_url": place_info.get("image_url"),
            "category": place_info.get("category") or "기타"
        })
    return formatted_data


def delete_bookmark(user_id: str, place_id: str) -> bool:
    supabase = get_supabase()
    try:
        result = supabase.table("bookmarks") \
            .delete() \
            .eq("place_id", place_id) \
            .eq("user_id", user_id) \
            .execute()
            
        return len(result.data) > 0
    except Exception as e:
        print(f"❌ 즐겨찾기 삭제 중 에러 발생: {e}")
        return False


def delete_saved_route(user_id: str, route_id: str) -> bool:
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
