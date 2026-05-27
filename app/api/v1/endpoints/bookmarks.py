from fastapi import APIRouter, Depends, HTTPException, status
from app.core.jwt import get_current_user
from app.schemas.bookmarks import BookmarkAddRequest, BookmarkedPlaceResponse
from app.services import bookmark_service 

router = APIRouter(prefix="/bookmarks")

@router.post("", status_code=status.HTTP_201_CREATED, summary="장소 찜하기")
async def add_bookmark(request_data: BookmarkAddRequest, user_id: str = "5fd0d467-03cb-4364-b8da-bb1d94d32f35"):
    success = bookmark_service.add_bookmark(user_id, request_data)
    if not success:
        raise HTTPException(status_code=500, detail="즐겨찾기 추가에 실패했습니다.")
    return {"message": "장소가 즐겨찾기에 성공적으로 추가되었습니다."}

@router.get("", response_model=list[BookmarkedPlaceResponse], summary="찜한 장소 목록 조회")
async def get_bookmarked_places(folder_name: str | None = None, user_id: str = "5fd0d467-03cb-4364-b8da-bb1d94d32f35"):
    return bookmark_service.get_bookmarked_places(user_id, folder_name)

@router.delete("/{bookmark_id}", summary="찜한 장소 삭제")
async def delete_bookmark(bookmark_id: str, user_id: str = "5fd0d467-03cb-4364-b8da-bb1d94d32f35"):
    success = bookmark_service.delete_bookmark(user_id, bookmark_id)
    if not success:
        raise HTTPException(status_code=404, detail="삭제할 권한이 없거나 존재하지 않는 즐겨찾기입니다.")
    return {"message": "즐겨찾기가 성공적으로 삭제되었습니다."}