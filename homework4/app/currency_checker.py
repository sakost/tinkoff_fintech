import random
import time
from decimal import Decimal
from functools import lru_cache
from math import lcm
from threading import Thread
from typing import Any, Callable, ContextManager

from sqlalchemy.orm import Session

from .models import Currency, CurrencyHistory


class CurrencyChecker(Thread):
    def __init__(
        self,
        sleep_time: int,
        percent_range_change: tuple[Decimal, Decimal],
        db_session: Callable[[], ContextManager[Session]],
        name: str = 'currency_checker',
        **kwargs: Any
    ):
        super().__init__(name=name, daemon=True, **kwargs)
        percent_minimum_change, percent_maximum_change = percent_range_change

        self._sleep_time = sleep_time
        self._min_change = percent_minimum_change
        self._max_change = percent_maximum_change

        self._db_session_factory = db_session

    def run(self) -> None:
        while True:
            time.sleep(self._sleep_time)

            with self._db_session_factory() as session:
                for currency in session.query(Currency).all():
                    percent_change = self.get_random_decimal(
                        self._min_change, self._max_change
                    )
                    currency.exchange_rate *= 1 + percent_change
                    history = CurrencyHistory(
                        currency_id=currency.id, exchange_rate=currency.exchange_rate
                    )
                    session.add(history)

    @classmethod
    def get_random_decimal(cls, from_: Decimal, to: Decimal) -> Decimal:
        lcm_numbers = cls._get_decimal_lcm(from_, to)
        rand_int = random.randint(int(lcm_numbers * from_), int(lcm_numbers * to))
        return Decimal(rand_int) / Decimal(lcm_numbers)

    @staticmethod
    @lru_cache(1, True)
    def _get_decimal_lcm(lhs: Decimal, rhs: Decimal) -> int:
        return lcm(lhs.as_integer_ratio()[1], rhs.as_integer_ratio()[1])
