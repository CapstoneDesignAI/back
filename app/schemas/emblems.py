from pydantic import BaseModel
from typing import Optional

class EmblemItem(BaseModel):
    emblem_id: str
    name: str
    description: str
    image_url: str
    unlock_stamp_threshold: int
    is_acquired: bool
    acquired_at: Optional[str] = None