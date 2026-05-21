from typing import Any
from pydantic import BaseModel, Field

class UserData(BaseModel):
    id: str
    nickName: str
    email: str
    profile_img: str | None = None
