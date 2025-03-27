from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr


class TimeStamp(BaseModel):
    created_at: datetime
    updated_at: datetime


class Permission(BaseModel):
    id: int
    name: str
    description: str


class Role(BaseModel):
    id: int
    name: str
    description: str
    permissions: List[Permission]


class UserInDBBase(TimeStamp):
    id: int
    username: EmailStr
    role_id: int


class UserInDB(UserInDBBase):
    password: str


class MeUser(UserInDBBase):
    role: Role


class UpdateUserBody(BaseModel):
    username: EmailStr | None = None


class UpdateUserRoleBody(BaseModel):
    role: str
