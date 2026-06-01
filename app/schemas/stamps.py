from pydantic import BaseModel

class StampBoardResponse(BaseModel):
    region_id: str
    region_name: str
    collected_stamps: int
    total_stamps: int = 10
    next_reward_text: str