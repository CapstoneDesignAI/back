from fastapi import APIRouter, Depends, HTTPException, status
from app.core.jwt import get_current_user
from app.schemas.bookmarks import BookmarkAddRequest, BookmarkAddResponse, BookmarkedPlaceResponse
from app.services import bookmark_service 

router = APIRouter(prefix="/bookmarks")

@router.post(
    "",
    response_model=BookmarkAddResponse,
    status_code=status.HTTP_201_CREATED,
    summary="장소 찜하기",
)
def add_bookmark(payload: BookmarkAddRequest, user_id: str = Depends(get_current_user)):
    success = bookmark_service.add_bookmark(user_id, payload)
    if not success:
        raise HTTPException(status_code=500, detail="즐겨찾기 추가에 실패했습니다.")
    return success

@router.get("", response_model=list[BookmarkedPlaceResponse], summary="찜한 장소 목록 조회")
def get_bookmarked_places(folder_id: str | None = None, user_id: str = Depends(get_current_user)):
    return bookmark_service.get_bookmarked_places(user_id, folder_id)

@router.delete("/{bookmark_id}", summary="찜한 장소 삭제")
def delete_bookmark(bookmark_id: str, user_id: str = Depends(get_current_user)):
    success = bookmark_service.delete_bookmark(user_id, bookmark_id)
    if not success:
        raise HTTPException(status_code=404, detail="삭제할 권한이 없거나 존재하지 않는 즐겨찾기입니다.")
    return {"message": "즐겨찾기가 성공적으로 삭제되었습니다."}
