from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import user_crud
from app.schema import LoginResponse, MeUser
from app.util.auth.token import ApiToken


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

    async def authenticate(self) -> LoginResponse:
        """Sign in request - Authentication

        Raises:
            HTTPException: Based on the type of error

        Returns:
            dict: OTP sent successfully
        """

        user = await user_crud.authenticate(
            self.db,
            username=self.username,
            password=self.password,
        )

        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        # return jsonable_encoder(user)
        me = MeUser(**jsonable_encoder(user))
        token = self.generate_token(userObj=me)

        return LoginResponse(
            id=int(user.id),
            access_token=token,
            msg="Login successful without OTP",
            me=me,
        )
