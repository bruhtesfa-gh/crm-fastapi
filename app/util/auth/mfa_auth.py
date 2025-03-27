from app.schema.index import MeUser
from app.schema.index import MeUser
from app.util.auth.token import ApiToken
import arrow
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud


class MFAAuth(ApiToken):
    """
    Main authentication class for Multi-Factor Authentication
    """

    def __init__(
        self,
        db: AsyncSession,
        username: str,
        password: str,
    ):
        self.username = username
        self.password = password
        self.db = db
        super().__init__()

    def authenticate(self) -> dict:
        """Sign in request - Authentication

        Raises:
            HTTPException: Based on the type of error

        Returns:
            dict: OTP sent successfully
        """

        user = crud.user.authenticate(
            self.db,
            email=self.username,
            password=self.password,
        )

        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        me = MeUser(**jsonable_encoder(user))
        token = self.generate_token(userObj=me)
        return dict(
            user_id=user.id,
            access_token=token,
            msg="Login successful without OTP",
            me=me
        )