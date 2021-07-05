import os

from todo_list.utils import FilterStatus

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SECRET_KEY = 'dev'
    DEBUG = False
    TESTING = False

    TASK_SUCCESSFULLY_ADDED_MESSAGE = 'Task successfully added'
    EMPTY_TASK_MESSAGE = 'Empty task description'

    DEFAULT_ITEMS_PER_PAGE = 10
    DEFAULT_FILTER_STATUS = FilterStatus.ACTIVE
    DEFAULT_TASK_DESCRIPTION = ''

    # database configs
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEVELOPMENT = True


class ProductionConfig(BaseConfig):
    SECRET_KEY = '355885e88cb64f2a93799055de6741d3'


class TestConfig(ProductionConfig):
    TESTING = True
    SERVER_NAME = 'localhost'
