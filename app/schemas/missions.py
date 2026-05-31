from pydantic import BaseModel

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