from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class TimeStamp(BaseModel):
    created_at: datetime
    updated_at: datetime


class Permission(BaseModel):
    id: int
    name: str
    description: str


class RoleBase(BaseModel):
    id: int
    name: str
    description: str


class RoleCreate(BaseModel):
    name: str
    description: str
    permissions: List[int]


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[int]] = None


class Role(RoleBase):
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
