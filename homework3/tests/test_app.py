from config import BaseConfig, TestConfig
from todo_list.app import create_app


def test_config():
    assert not create_app().testing
    assert not create_app(BaseConfig).testing
    assert create_app(TestConfig).testing
