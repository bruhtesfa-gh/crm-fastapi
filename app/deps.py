from typing import Any, Generator, Optional, cast

from fastapi import Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import UUID4, ValidationError
from app.util.setting import get_settings
from app.schema.index import TokenPayload
from app.models import User

settings = get_settings()

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/auth/login/access-token"
)

# Function to verify the access token extracted from the request
def verify_access_token(token: str) -> TokenPayload:
    try:
        # Decode and verify the token using the secret key and algorithm
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )



def get_auth_user(
    request: Request, token: str = Depends(reusable_oauth2)
) -> User:
    if not request:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )
    if request.state.sub == "anonymous":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    return User(**jsonable_encoder(request.state.user), hashed_password="dummy")