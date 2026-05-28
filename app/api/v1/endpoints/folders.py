from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.folders import FolderCreateRequest, FolderResponse, FolderUpdateRequest
from app.services import folder_service
from app.core.jwt import get_current_user 

router = APIRouter(prefix="/folders")

@router.post(
    "", 
    response_model=FolderResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="즐겨찾기 폴더 생성"
)
def create_new_folder(
    request_data: FolderCreateRequest, 
    user_id: str = Depends(get_current_user)
):
    result = folder_service.create_folder(user_id, request_data)
    if not result:
        raise HTTPException(status_code=500, detail="폴더 생성에 실패했습니다.")
    return result


@router.get(
    "", 
    response_model=list[FolderResponse], 
    summary="즐겨찾기 폴더 목록 조회"
)
def read_all_folders(user_id: str = Depends(get_current_user)):
    return folder_service.get_folders(user_id)

@router.put("/{folder_id}", summary="즐겨찾기 폴더 이름 수정")
def modify_folder(
    folder_id: str,
    request_data: FolderUpdateRequest,
    user_id: str = Depends(get_current_user)
):
    success = folder_service.update_folder(user_id, folder_id, request_data)
    if not success:
        raise HTTPException(status_code=400, detail="폴더 수정에 실패했거나 권한이 없습니다.")
    return {"message": "폴더 이름이 성공적으로 수정되었습니다."}


@router.delete("/{folder_id}", summary="즐겨찾기 폴더 삭제")
def remove_folder(
    folder_id: str,
    user_id: str = Depends(get_current_user)
):
    success = folder_service.delete_folder(user_id, folder_id)
    if not success:
        raise HTTPException(status_code=400, detail="기본 폴더는 삭제할 수 없거나 폴더 삭제에 실패했습니다.")
    return {"message": "폴더가 성공적으로 삭제되었습니다."}