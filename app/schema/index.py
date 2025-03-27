from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class TimeStamp(BaseModel):
    created_at: datetime
    updated_at: datetime

class Role(BaseModel):
    id: int
    name: str
    description: str

class UserInDBBase(TimeStamp):
    id: int
    username: str
    role_id: int

class UserInDB(UserInDBBase):
    password: str

class MeUser(UserInDBBase):
    role: Role

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    user: MeUser