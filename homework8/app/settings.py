from enum import Enum

from pydantic import AnyUrl, BaseSettings


class SettingsEnum(Enum):
    PRODUCTION = 'production'
    DEVELOPMENT = 'development'
    TESTING = 'testing'


class EnvironmentSettings(BaseSettings):
    CONFIG_TYPE: SettingsEnum

    class Config:
        env_file = '.env'


class ProductionSettings(EnvironmentSettings):
    REDIS_URL: AnyUrl
    DEBUG: bool = False
    TESTING: bool = False


class DevelopmentSettings(ProductionSettings):
    DEBUG = True


class TestingSettings(ProductionSettings):
    TESTING = True


def get_settings() -> ProductionSettings:
    config_type = EnvironmentSettings().CONFIG_TYPE
    if config_type == SettingsEnum.DEVELOPMENT:
        return DevelopmentSettings()
    if config_type == SettingsEnum.PRODUCTION:
        return ProductionSettings()
    return TestingSettings()


settings = get_settings()
