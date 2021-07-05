from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from unittest import mock

import pytest

from app.bot import (
    determine_operation,
    get_user,
    main,
    register_user,
    sell_all,
    try_operation,
)
from app.models import TypeWalletOperation
from app.schemas import CurrencyModel, CurrencyWalletModel, UserModel


@mock.patch('requests.get')
@mock.patch('app.schemas.UserModel')
def test_get_user(mock_user_model, mock_get) -> None:
    mock_get.return_value = mock_get
    mock_get.json.return_value = {'data': {}}

    get_user('user')

    assert mock_get.called_once
    assert mock_get.raise_for_status.called_once
    mock_get.assert_called_once_with(
        'http://localhost:5000/user/get_info', params={'name': 'user'}
    )
    mock_user_model.assert_called_once_with()


@mock.patch('requests.post')
@mock.patch('app.schemas.UserModel')
def test_success_register_user(mock_user_model, mock_post) -> None:
    mock_post.return_value = mock_post
    mock_post.json.return_value = {'data': {}}
    mock_post.status_code = HTTPStatus.OK

    register_user('user')

    mock_user_model.assert_called_once_with()
    mock_post.assert_called_once()


@mock.patch('requests.post')
@mock.patch('app.schemas.UserModel')
@mock.patch('app.bot.get_user')
def test_fail_register_user(mock_get_user, mock_user_model, mock_post) -> None:
    mock_post.return_value = mock_post
    mock_post.json.return_value = {'data': {}}
    mock_post.status_code = HTTPStatus.FORBIDDEN

    register_user('user')

    assert mock_user_model.called == 0
    mock_post.assert_called_once()
    assert mock_get_user.called_once


def test_determine_operation() -> None:
    assert determine_operation(Decimal(0), Decimal(1)) == TypeWalletOperation.SELL
    assert determine_operation(Decimal(1), Decimal(1)) == TypeWalletOperation.BUY
    assert determine_operation(Decimal(1), Decimal(0)) == TypeWalletOperation.BUY


@mock.patch('requests.post')
def test_success_try_operation(mock_post) -> None:
    mock_post.return_value = mock_post
    mock_post.status_code = HTTPStatus.OK
    mock_post.json.return_value = {'status': 'ok'}

    assert try_operation(1, 'USD', TypeWalletOperation.BUY)
    assert mock_post.raise_for_status.called == 1


@mock.patch('requests.post')
def test_fail_try_operation(mock_post) -> None:
    mock_post.return_value = mock_post
    mock_post.status_code = HTTPStatus.FORBIDDEN
    mock_post.json.return_value = {'status': 'ok'}

    ans = try_operation(1, 'USD', TypeWalletOperation.BUY)
    assert mock_post.raise_for_status.called == 0
    assert not ans


@mock.patch('requests.post')
def test_sell_all(mock_post) -> None:
    mock_post.return_value = mock_post
    user = UserModel(
        id=1,
        name='user',
        balance=Decimal('0'),
        reg_date=datetime.utcfromtimestamp(1),
        currency_wallets=[
            CurrencyWalletModel(
                currency_id=1,
                balance=Decimal('1.0'),
                currency=CurrencyModel(id=1, name='USD', exchange_rate=Decimal('1.0')),
            )
        ],
    )
    sell_all(user)

    mock_post.assert_called_once()
    mock_post.raise_for_status.assert_called_once()


@pytest.mark.parametrize(
    'return_value,call_count',
    [
        [True, 0],
        [False, 1],
    ],
)
def test_main(return_value, call_count) -> None:
    with mock.patch('warnings.warn') as mock_warn, mock.patch(
        'app.bot.maximize_profit'
    ) as mock_maximize_profit, mock.patch(
        'app.bot.register_user'
    ) as mock_register_user:
        mock_register_user.return_value = (return_value, None)
        main()
        assert mock_warn.call_count == call_count
        mock_maximize_profit.assert_called_once_with(None)
        mock_register_user.assert_called_once()
