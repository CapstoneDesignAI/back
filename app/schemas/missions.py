from pydantic import BaseModel

class MissionListItem(BaseModel):
    mission_id: str
    title: str
    stamp_count: int
    difficulty: str
    is_completed: bool