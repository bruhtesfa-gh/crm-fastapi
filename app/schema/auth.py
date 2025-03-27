from typing import Optional

from pydantic import BaseModel, EmailStr

from app.schema.user import MeUser


class LoginResponse(BaseModel):
    id: int
    access_token: str
    msg: str
    me: MeUser


class RegisterBody(BaseModel):
    username: EmailStr
    password: str
    role: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    user: MeUser
