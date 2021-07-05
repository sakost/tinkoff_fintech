# pylint: disable=too-many-lines
# type: ignore[type-arg]
from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from typing import Optional

import pytest
from flask import Flask, url_for
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from app import views
from app.models import Currency, CurrencyHistory, CurrencyWallet, User
from app.schemas import ResponseModel, UserModel
from app.utils import StatusType


def test_user_get_info(client: FlaskClient, user: User) -> None:
    response = client.get(url_for('view.user_get_info', **{'id': user.id}))

    assert response.status_code == HTTPStatus.OK
    assert ResponseModel(**response.get_json()) == ResponseModel(
        **{
            'status': 'ok',
            'data': {
                'id': user.id,
                'name': user.name,
                'balance': float(user.balance),
                'reg_date': user.reg_date,
                'currency_wallets': [],
            },
            'error': None,
        }
    )


def test_user_get_info_error(client: FlaskClient) -> None:
    assert client.get('/user/get_info').status_code == HTTPStatus.NOT_FOUND
    assert (
        client.get(url_for('view.user_get_info', **{'id': 1})).status_code
        == HTTPStatus.NOT_FOUND
    )


def test_user_register(client: FlaskClient, db_session: Session) -> None:
    response = client.post(
        '/user/register',
        json={
            'name': 'user',
        },
    )

    user = db_session.query(User).get(1)

    assert response.status_code == HTTPStatus.OK
    assert ResponseModel(**response.get_json()) == ResponseModel(
        **{
            'status': 'ok',
            'data': UserModel.from_orm(user),
        }
    )


def test_user_register_invalid_name(client: FlaskClient) -> None:
    response = client.post(
        '/user/register',
        json={
            'name': 'u',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_json() == {
        'validation_error': {
            'body_params': [
                {
                    'ctx': {'limit_value': 3},
                    'loc': ['name'],
                    'msg': 'ensure this value has at least 3 characters',
                    'type': 'value_error.any_str.min_length',
                }
            ]
        }
    }


def test_user_register_user_already_exists(
    client: FlaskClient, db_session: Session
) -> None:
    db_session.add(User(id=1, name='user', balance=Decimal('1000')))
    db_session.commit()
    response = client.post(
        '/user/register',
        json={
            'name': 'user',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_json() == {
        'status': 'error',
        'error': 'User already exists',
        'data': None,
    }


def test_currency_get_info(client: FlaskClient, currency: Currency) -> None:
    response = client.get(
        url_for(
            'view.get_currency_info',
            **{
                'name': currency.name,
            },
        ),
    )
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['data']['id'] == currency.id
    assert data['data']['exchange_rate'] == float(currency.exchange_rate)


def test_currency_get_info_error(client: FlaskClient) -> None:
    assert (
        client.get(
            url_for(
                'view.get_currency_info',
                **{
                    'name': 'INVALID_NAME',
                },
            ),
        ).status_code
        == HTTPStatus.NOT_FOUND
    )


def test_currency_get_all(app: Flask, client: FlaskClient) -> None:
    with app.db_session() as session:
        session.add(Currency(id=1, name='USD', exchange_rate=Decimal('1.0')))
        session.add(Currency(id=2, name='RUB', exchange_rate=Decimal('10.0')))

    assert client.get('/currency/all').get_json() == {
        'status': 'ok',
        'data': [
            {'exchange_rate': 1.0, 'id': 1, 'name': 'USD'},
            {'exchange_rate': 10.0, 'id': 2, 'name': 'RUB'},
        ],
        'error': None,
    }


def test_currency_add(client: FlaskClient, db_session: Session) -> None:
    assert (
        client.post(
            '/currency/add',
            json={
                'name': 'USD',
            },
        ).status_code
        == HTTPStatus.OK
    )
    currency = db_session.query(Currency).filter(Currency.name == 'USD').first()
    assert currency is not None
    assert currency.name == 'USD'


def test_currency_add_error(client: FlaskClient, db_session: Session) -> None:
    db_session.add(
        Currency(id=1, name='USD', exchange_rate=Currency.generate_exchange_rate())
    )
    response = client.post('/currency/add', json={'name': 'USD'})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.get_json() == {
        'status': 'error',
        'error': 'This name currency is already exists or name is invalid',
        'data': None,
    }


def test_has_new_exchange(currency: Currency, db_session: Session) -> None:
    db_session.add(
        CurrencyHistory(
            id=1,
            currency_id=currency.id,
            exchange_rate=currency.exchange_rate,
            datetime=datetime.utcfromtimestamp(2),
        )
    )
    db_session.commit()

    assert views.has_new_exchange(db_session, 1)
    assert not views.has_new_exchange(db_session, 3)


@pytest.mark.parametrize(
    'cost,balance,passed',
    [
        [Decimal(1), Decimal(0), False],
        [Decimal(999), Decimal(1000), True],
        [Decimal(1001), Decimal(1000), False],
    ],
)
def test_buy(
    db_session: Session, cost: Decimal, balance: Decimal, passed: bool
) -> None:
    db_session.add(User(id=1, name='user', balance=balance))
    db_session.add(Currency(id=1, name='USD', exchange_rate=cost))
    db_session.commit()

    user = db_session.query(User).get(1)
    currency = db_session.query(Currency).get(1)
    assert user is not None
    assert currency is not None

    response = views.buy(db_session, user, currency, Decimal(1))
    if isinstance(response, tuple):
        assert passed == (response[0].status == StatusType.OK)
    elif isinstance(response, ResponseModel):
        assert passed == (response.status == StatusType.OK)  # pylint: disable=no-member
    else:
        raise AssertionError(f'Unknown response type: {type(response)}')


@pytest.mark.parametrize(
    'cost,balance,passed',
    [
        [Decimal(1), Decimal('0'), False],
        [Decimal(1), Decimal('0.1'), False],
        [Decimal(1), Decimal('1'), True],
        [Decimal(9), Decimal('10'), True],
    ],
)
def test_sell(db_session: Session, cost: Decimal, balance: Decimal, passed: bool):
    currency = Currency(id=1, name='USD', exchange_rate=cost)
    db_session.add(currency)
    db_session.add(User(id=1, name='user', balance=Decimal(0)))
    db_session.add(CurrencyWallet(id=1, balance=balance, currency=currency, user_id=1))
    db_session.commit()

    user = db_session.query(User).get(1)
    currency: Optional[Currency] = db_session.query(Currency).first()
    assert user is not None
    assert currency is not None

    response = views.sell(db_session, user, currency, Decimal(1))

    if isinstance(response, tuple):
        assert passed == (response[0].status == StatusType.OK)
    elif isinstance(response, ResponseModel):
        assert passed == (response.status == StatusType.OK)  # pylint: disable=no-member
    else:
        raise AssertionError(f'Unknown response type: {type(response)}')


def test_client_invalid_operation(client: FlaskClient, db_session: Session):
    assert (
        client.post(
            '/currency/operation',
            json={
                'operation': 'sell',
                'user_id': 1,
                'currency_name': 'INV',
                'count': '1',
                'timestamp': 1,
            },
        ).status_code
        == HTTPStatus.NOT_FOUND
    )
    db_session.add(User(id=1, name='user', balance=Decimal(0)))
    db_session.commit()

    assert (
        client.post(
            '/currency/operation',
            json={
                'operation': 'sell',
                'user_id': 1,
                'currency_name': 'INV',
                'count': '1',
                'timestamp': 1,
            },
        ).status_code
        == HTTPStatus.NOT_FOUND
    )


@pytest.mark.parametrize(
    'cost,balance,count,passed',
    [
        [Decimal('10'), Decimal('1'), Decimal('0.1'), True],
        [Decimal('10'), Decimal('1'), Decimal('1'), False],
        [Decimal('10'), Decimal('100'), Decimal('1'), True],
        [Decimal('10'), Decimal('100'), Decimal('10'), True],
        [Decimal('10'), Decimal('100'), Decimal('10.1'), False],
    ],  # pylint: disable = too-many-arguments
)
def test_client_buy(
    db_session: Session,
    client: FlaskClient,
    cost: Decimal,
    balance: Decimal,
    count: Decimal,
    passed: bool,
):
    currency = Currency(id=1, name='USD', exchange_rate=cost)
    user = User(id=1, name='user', balance=balance)
    db_session.add(currency)
    db_session.add(user)
    db_session.commit()

    response = client.post(
        '/currency/operation',
        json={
            'operation': 'buy',
            'user_id': user.id,
            'currency_name': currency.name,
            'count': f'{count:.10f}',
            'timestamp': 1,
        },
    )

    assert (response.status_code == HTTPStatus.OK) == passed
