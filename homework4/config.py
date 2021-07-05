import os
from decimal import Decimal


class BaseConfig:
    SECRET_KEY = 'dev'
    DEBUG = False
    TESTING = False

    WORKER_SLEEP_TIME = 10  # in secs

    PERCENT_COMMISSION = Decimal('0.05')
    PERCENT_MINIMUM_CHANGE = Decimal('-0.1')
    PERCENT_MAXIMUM_CHANGE = Decimal('0.1')

    REGISTRATION_DATETIME_FORMAT = '%S:%M:%H %d.%m.%Y'

    DEFAULT_CURRENCIES_COUNT = 5
    ADD_DEFAULT_CURRENCIES = True

    # database configs
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEVELOPMENT = True


class ProductionConfig(BaseConfig):
    SECRET_KEY = '355885e88cb64f2a93799055de6741d3'


class TestConfig(BaseConfig):
    TESTING = True
    SERVER_NAME = 'localhost'
    PERCENT_COMMISSION = Decimal('0')
    ADD_DEFAULT_CURRENCIES = False
