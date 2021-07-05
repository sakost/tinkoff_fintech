from enum import Enum

from pydantic import BaseSettings


class SettingsEnum(Enum):
    PRODUCTION = 'production'
    DEVELOPMENT = 'development'
    TESTING = 'testing'


class EnvironmentSettings(BaseSettings):
    CONFIG_TYPE: SettingsEnum

    class Config:
        env_file = '.env'


class ProductionSettings(EnvironmentSettings):
    SQLALCHEMY_DATABASE_URI: str
    DEBUG: bool = False
    TESTING: bool = False


class DevelopmentSettings(ProductionSettings):
    DEBUG = True


class TestingSettings(ProductionSettings):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


def get_settings() -> ProductionSettings:
    config_type = EnvironmentSettings().CONFIG_TYPE
    if config_type == SettingsEnum.DEVELOPMENT:
        return DevelopmentSettings()  # pragma: no cover
    if config_type == SettingsEnum.PRODUCTION:
        return ProductionSettings()  # pragma: no cover
    return TestingSettings()


settings = get_settings()
