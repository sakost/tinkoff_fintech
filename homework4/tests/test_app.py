from unittest import mock

from app.app import create_app, start_currency_checker
from config import ProductionConfig, TestConfig


def test_config() -> None:
    assert not create_app().testing
    assert not create_app(ProductionConfig).testing
    assert create_app(TestConfig).testing


@mock.patch('app.currency_checker.CurrencyChecker')
def test_start_currency_checker(mocked_checker) -> None:
    start_currency_checker()
    assert mocked_checker.called_once
    assert mocked_checker.start.called_once
