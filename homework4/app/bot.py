import logging
import time
import warnings
from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from typing import Any

import requests
from urllib3.util import parse_url

from . import schemas
from .models import TypeWalletOperation

HOST_URL = parse_url('http://localhost:5000')
SLEEP_TIME = 3
DEFAULT_OP_COUNT = 1.0

logger = logging.getLogger()


def get_user(username: str = 'bot') -> schemas.UserModel:
    response = requests.get(
        f'{HOST_URL}/user/get_info',
        params={'name': username},
    )
    response.raise_for_status()
    return schemas.UserModel(**response.json()['data'])


def register_user(username: str = 'bot') -> tuple[bool, schemas.UserModel]:
    response = requests.post(
        f'{HOST_URL.url}/user/register',
        json={
            'name': username,
        },
    )
    if response.status_code != HTTPStatus.OK:
        return False, get_user()
    return True, schemas.UserModel(**response.json()['data'])


def determine_operation(
    previous_cost: Decimal, current_cost: Decimal
) -> TypeWalletOperation:
    if previous_cost < current_cost:
        return TypeWalletOperation.SELL
    return TypeWalletOperation.BUY


def try_operation(
    user_id: int, currency_name: str, operation: TypeWalletOperation
) -> bool:
    response = requests.post(
        f'{HOST_URL.url}/currency/operation',
        json={
            'operation': operation.value,
            'user_id': user_id,
            'currency_name': currency_name,
            'count': DEFAULT_OP_COUNT,
            'timestamp': datetime.now().timestamp(),
        },
    )
    if response.status_code == HTTPStatus.FORBIDDEN:
        return False
    response.raise_for_status()
    return response.json()['status'] == 'ok'


def parse_currencies(data: dict[str, Any]) -> list[schemas.CurrencyModel]:
    return list(map(lambda x: schemas.CurrencyModel(**x), data['data']))


def maximize_profit(user: schemas.UserModel) -> None:
    response = requests.get(f'{HOST_URL}/currency/all')
    response.raise_for_status()
    cached_currencies = parse_currencies(response.json())

    while True:
        time.sleep(SLEEP_TIME)
        response = requests.get(f'{HOST_URL}/currency/all')
        response.raise_for_status()
        currencies = parse_currencies(response.json())

        for num, currency in enumerate(currencies):
            try_operation(
                user.id,
                currency.name,
                determine_operation(
                    cached_currencies[num].exchange_rate, currency.exchange_rate
                ),
            )
        cached_currencies = currencies


def sell_all(user: schemas.UserModel) -> None:
    if user.currency_wallets is None:
        return
    for wallet in user.currency_wallets:
        if wallet.currency is None:  # pragma: no cover
            continue
        response = requests.post(
            f'{HOST_URL}/currency/operation',
            json={
                'operation': TypeWalletOperation.SELL.value,
                'user_id': user.id,
                'currency_name': wallet.currency.name,
                'count': float(wallet.balance),
                'timestamp': datetime.now().timestamp(),
            },
        )
        response.raise_for_status()


def main() -> None:
    try:
        registered, user = register_user()
    except requests.exceptions.HTTPError:
        logger.exception('Invalid status returned')
        return
    if not registered:
        warnings.warn('User already exists, using existing account')
    try:
        maximize_profit(user)
    except KeyboardInterrupt:
        sell_all(get_user())
        logger.info('Exiting')


if __name__ == '__main__':  # pragma: no cover
    main()
