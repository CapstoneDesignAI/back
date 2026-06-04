from pydantic import BaseModel, Field


class PlaceCreateRequest(BaseModel):
    kakao_place_id: str = Field(..., description="카카오 장소 ID")
    name: str = Field(..., description="장소명")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    address: str 
    category: str 

class PlaceCreateResponse(BaseModel):
    message: str
    place_id: str
    is_newly_created: bool
