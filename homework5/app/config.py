from typing import Any

from pydantic import BaseSettings

from .utils import singleton_cache


class Settings(BaseSettings):
    TESTING: bool = False

    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///db.sqlite3'

    FIRST_SUPERUSER: str = 'admin'
    FIRST_SUPERUSER_PASSWORD: str = 'admin'
    FIRST_SUPERUSER_ROLE: str = 'superuser'
    USER_ROLE_NAME = 'user'

    OBJECTS_PER_PAGE: int = 100

    class Config:
        case_sensitive = True
        env_file = '.env'


@singleton_cache
def get_settings(**kwargs: Any) -> Settings:
    return Settings(**kwargs)
