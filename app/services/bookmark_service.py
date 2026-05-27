from app.db.base import get_supabase
from app.schemas.bookmarks import BookmarkAddRequest, BookmarkedPlaceResponse

def add_bookmark(user_id: str, request_data: BookmarkAddRequest) -> bool:
    supabase = get_supabase()
    try:
        target_folder_name = request_data.folder_name if request_data.folder_name else "기본 폴더"

        supabase.table("bookmarks").insert({
            "user_id": user_id,
            "folder_name": target_folder_name,
            "place_id": request_data.place_id
        }).execute()
        
        return True
    except Exception as e:
        print(f"❌ 즐겨찾기 추가 중 에러 발생: {e}")
        return False


def get_bookmarked_places(user_id: str, folder_name: str | None = None) -> list[BookmarkedPlaceResponse]:
    supabase = get_supabase()

    query = supabase.table("bookmarks").select("id, folder_name, place_id, places(name, address, image_url, category)").eq("user_id", user_id)
    
    if folder_name:
        query = query.eq("folder_name", folder_name)
        
    result = query.execute()
    
    formatted_data = []
    for row in result.data:
        place_info = row.get("places") or {}
        formatted_data.append({
            "bookmark_id": str(row["id"]),
            "folder_name": row["folder_name"],
            "place_id": row["place_id"],
            "name": place_info.get("name") or "이름 없음",
            "address": place_info.get("address") or "주소 없음",
            "image_url": place_info.get("image_url"),
            "category": place_info.get("category") or "기타"
        })
    return formatted_data


def delete_bookmark(user_id: str, bookmark_id: str) -> bool:
    supabase = get_supabase()
    try:
        result = supabase.table("bookmarks") \
            .delete() \
            .eq("id", bookmark_id) \
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