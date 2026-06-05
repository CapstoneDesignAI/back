from pydantic import BaseModel, Field, model_validator

from app.schemas.places import PlaceCreateRequest

class FolderCreateRequest(BaseModel):
    name: str = Field(..., description="생성할 폴더 이름", example="강릉 맛집 투어")
    
class FolderResponse(BaseModel):
    folder_id: str
    name: str
    is_default: bool
    bookmark_count: int
    
class BookmarkAddRequest(BaseModel):
    place_id: str | None = Field(None, description="찜할 장소 ID")
    place: PlaceCreateRequest | None = Field(
        None,
        description="DB에 없을 수 있는 카카오 장소 정보",
    )
    folder_id: str | None = Field(None, description="저장할 폴더 ID (비어두면 기본 폴더로 지정)")

    @model_validator(mode="after")
    def validate_place_reference(self):
        if not self.place_id and not self.place:
            raise ValueError("place_id 또는 place 중 하나는 필요합니다.")
        return self


class BookmarkAddResponse(BaseModel):
    message: str
    bookmark_id: str
    place_id: str
    is_newly_created_place: bool
    
class BookmarkedPlaceResponse(BaseModel):
    bookmark_id: str
    folder_id: str 
    place_id: str
    name: str
    address: str
    image_url: str | None = None
    category: str
