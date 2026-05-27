from pydantic import BaseModel, Field

class FolderCreateRequest(BaseModel):
    name: str = Field(..., description="생성할 폴더 이름", example="강릉 맛집 투어")
    
class FolderResponse(BaseModel):
    folder_id: str
    name: str
    is_default: bool
    bookmark_count: int
    
class BookmarkAddRequest(BaseModel):
    place_id: str = Field(..., description="찜할 장소 ID")
    folder_id: str | None = Field(None, description="저장할 폴더 ID (비어두면 기본 폴더로 지정)")
    
class BookmarkedPlaceResponse(BaseModel):
    bookmark_id: str
    folder_id: str | None = None
    place_id: str
    name: str
    address: str
    image_url: str | None = None
    category: str