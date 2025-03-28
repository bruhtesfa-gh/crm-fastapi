from typing import List

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from app.schema import MeUser, TokenPayload
from app.util.setting import get_settings

settings = get_settings()

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Function to verify the access token extracted from the request
def verify_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, str(settings.SECRET_KEY), algorithms=[str(settings.ALGORITHM)]
        )
        return TokenPayload(sub=str(payload["sub"]), user=MeUser(**payload["user"]))
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


def get_auth_user(request: Request, token: str = Depends(reusable_oauth2)) -> MeUser:
    payload = verify_access_token(token)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )
    request.state.sub = payload.sub
    request.state.user = payload.user

    return MeUser(**payload.user.__dict__)


def get_role_user(required_role: List[str]):
    def dependency(auth_user: MeUser = Depends(get_auth_user)) -> MeUser:
        if auth_user.role.name not in required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privileges. {', '.join(required_role)} role required.",
            )
        return auth_user

    return dependency
