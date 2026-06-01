from pydantic import BaseModel
from typing import Optional

class MissionListItem(BaseModel):
    mission_id: str
    title: str
    stamp_count: int
    difficulty: str
    is_completed: bool
    
class MissionDetailResponse(BaseModel):
    mission_id: str
    region_id: str
    title: str
    description: str | None
    reward_stamp_count: int
    difficulty: str
    distance_text: str
    
    place_name: str
    lat: float
    lng: float
    
    is_completed: bool
    
class MissionVerifyRequest(BaseModel):
    latitude: float
    longitude: float
    image_url: Optional[str] = None

class MissionVerifyResponse(BaseModel):
    message: str
    user_mission_id: str
    status: str