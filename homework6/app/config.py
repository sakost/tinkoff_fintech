from typing import Any

from pydantic import AnyUrl, BaseSettings

from .utils import singleton_cache


class Settings(BaseSettings):
    REDIS_URL: AnyUrl
    DEBUG: bool = False
    TESTING: bool = False

    class Config:
        env_file = '.env'


@singleton_cache
def settings(**kwargs: Any) -> Settings:
    return Settings(**kwargs)
