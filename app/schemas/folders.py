from pydantic import BaseModel, Field

class FolderCreateRequest(BaseModel):
    name: str = Field(..., description="생성할 폴더 이름", example="제주도 힐링 여행")

class FolderResponse(BaseModel):
    folder_id: str
    name: str
    is_default: bool
    bookmark_count: int = 0
    
class FolderUpdateRequest(BaseModel):
    name: str = Field(..., description="수정할 새 폴더 이름", example="강릉 카페 투어 ☕")