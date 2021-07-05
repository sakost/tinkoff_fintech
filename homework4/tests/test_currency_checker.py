# pylint: disable=protected-access
from decimal import Decimal

from flask import Flask

from app.currency_checker import CurrencyChecker


def test_creation(app: Flask) -> None:
    assert CurrencyChecker(
        app.config['WORKER_SLEEP_TIME'],
        (app.config['PERCENT_MINIMUM_CHANGE'], app.config['PERCENT_MAXIMUM_CHANGE']),
        app.db_session,
    ).daemon


def test_decimals(app: Flask) -> None:
    cc = CurrencyChecker(
        app.config['WORKER_SLEEP_TIME'],
        (app.config['PERCENT_MINIMUM_CHANGE'], app.config['PERCENT_MAXIMUM_CHANGE']),
        app.db_session,
    )
    assert cc.get_random_decimal(Decimal('0.01'), Decimal('0.01')) == Decimal('0.01')
    assert cc._get_decimal_lcm(Decimal('-10'), Decimal('10')) == 1
