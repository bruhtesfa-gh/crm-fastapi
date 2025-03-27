from abc import ABC, abstractmethod
from datetime import timedelta

import arrow
from fastapi.encoders import jsonable_encoder
from jose import jwt

from app.util.setting import get_settings
from app.schema.index import MeUser
from app.util.constants import DEFAULT_TIMEZONE

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
        expires = now + self.delta
        exp = expires.timestamp()
        encoded_jwt = jwt.encode(
            {
                "exp": exp,
                "nbf": now,
                "sub": userObj.id,
                "user": jsonable_encoder(userObj),
                "type": self.type,
                "action": self.action,
            },
            settings.SECRET_KEY,
            algorithm="HS256",
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
