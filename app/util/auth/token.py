from abc import ABC, abstractmethod
from datetime import timedelta

import arrow
from fastapi.encoders import jsonable_encoder
from jose import jwt

from app.schema import MeUser
from app.util.constants import DEFAULT_TIMEZONE
from app.util.setting import get_settings

settings = get_settings()


class AppBaseToken(ABC):

    @property
    @abstractmethod
    def delta(self) -> timedelta:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @property
    @abstractmethod
    def action(self) -> str:
        pass

    # TODO bring Verify token method here

    def generate_token(self, userObj: MeUser) -> str:
        now = arrow.now(DEFAULT_TIMEZONE).datetime
        expires = now + timedelta(days=30)
        exp = expires.timestamp()
        encoded_jwt = jwt.encode(
            {
                "exp": exp,
                "nbf": now,
                "sub": str(userObj.id),
                "user": jsonable_encoder(userObj),
                "type": self.type,
                "action": self.action,
            },
            str(settings.SECRET_KEY),
            algorithm=str(settings.ALGORITHM),
        )
        return encoded_jwt


class ApiToken(AppBaseToken):

    @property
    def delta(self) -> timedelta:
        return timedelta(days=3)

    @property
    def type(self) -> str:
        return "api"

    @property
    def action(self) -> str:
        return "access"
