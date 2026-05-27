from app.db.base import get_supabase
from app.schemas.folders import FolderCreateRequest, FolderResponse, FolderUpdateRequest

def create_folder(user_id: str, request_data: FolderCreateRequest) -> FolderResponse | None:
    supabase = get_supabase()
    try:
        result = supabase.table("folders").insert({
            "user_id": user_id,
            "name": request_data.name,
            "is_default": False
        }).execute()
        
        if not result.data:
            return None
            
        new_folder = result.data[0]
        
        return FolderResponse(
            folder_id=str(new_folder["id"]),
            name=new_folder["name"],
            is_default=new_folder["is_default"],
            bookmark_count=0
        )
    except Exception as e:
        print(f"❌ 폴더 생성 중 에러 발생: {e}")
        return None

def get_folders(user_id: str) -> list[FolderResponse]:
    supabase = get_supabase()
    
    folders_res = supabase.table("folders").select("*").eq("user_id", user_id).execute()
    
    bookmarks_res = supabase.table("bookmarks").select("folder_id").eq("user_id", user_id).execute()
    
    bookmark_counts = {}
    for bm in bookmarks_res.data:
        fid = bm.get("folder_id")
        if fid:
            bookmark_counts[fid] = bookmark_counts.get(fid, 0) + 1

    formatted_folders = []
    for f in folders_res.data:
        formatted_folders.append(
            FolderResponse(
                folder_id=str(f["id"]),
                name=f["name"],
                is_default=f["is_default"],
                bookmark_count=bookmark_counts.get(f["id"], 0)
            )
        )
    return formatted_folders

def update_folder(user_id: str, folder_id: str, request_data: FolderUpdateRequest) -> bool:
    supabase = get_supabase()
    try:
        result = supabase.table("folders") \
            .update({"name": request_data.name}) \
            .eq("id", folder_id) \
            .eq("user_id", user_id) \
            .execute()
            
        return len(result.data) > 0
    except Exception as e:
        print(f"❌ 폴더 수정 중 에러 발생: {e}")
        return False

def delete_folder(user_id: str, folder_id: str) -> bool:
    supabase = get_supabase()
    try:
        folder_check = supabase.table("folders").select("is_default").eq("id", folder_id).execute()
        if folder_check.data and folder_check.data[0]["is_default"]:
            print("⚠️ 기본 폴더는 삭제할 수 없습니다.")
            return False

        result = supabase.table("folders") \
            .delete() \
            .eq("id", folder_id) \
            .eq("user_id", user_id) \
            .execute()
            
        return len(result.data) > 0
    except Exception as e:
        print(f"❌ 폴더 삭제 중 에러 발생: {e}")
        return False