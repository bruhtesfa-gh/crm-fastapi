from functools import lru_cache
from typing import Any

from dotenv import dotenv_values

# Load environment variables from the .env file
s = dotenv_values(".env")


class Settings:
    def __init__(self, data: Any) -> None:
        for key, value in data.items():
            setattr(self, key, value)


@lru_cache()
def get_settings() -> Any:
    """
    Get settings. ready for FastAPI's Depends.
    lru_cache - cache the Settings object per arguments given.
    """
    settings = Settings(s)
    return settings
