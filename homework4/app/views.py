from datetime import datetime
from decimal import Decimal
from http import HTTPStatus
from typing import Union

from flask import Blueprint
from flask import current_app as app
from flask_pydantic import validate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Currency, CurrencyHistory, CurrencyWallet, TypeWalletOperation, User
from .schemas import (
    CurrencyInfoModel,
    CurrencyModel,
    OperationModel,
    ResponseModel,
    UserInfoModel,
    UserModel,
    UserRegisterModel,
)
from .utils import StatusType

view_bp = Blueprint('view', __name__)


@view_bp.route('/currency/add', methods=['POST'])
@validate()
def add_currency(
    body: CurrencyInfoModel,
) -> Union[ResponseModel, tuple[ResponseModel, int]]:
    try:
        with app.db_session() as session:
            # noinspection PyTypeChecker
            currency = Currency(
                exchange_rate=Currency.generate_exchange_rate(), name=body.name
            )
            session.add(currency)
    except IntegrityError:
        return (
            ResponseModel(
                status=StatusType.ERROR,
                error='This name currency is already exists or name is invalid',
            ),
            HTTPStatus.BAD_REQUEST,
        )
    return ResponseModel(status=StatusType.OK)


@view_bp.route('/user/get_info', methods=['GET'])
@validate()
def user_get_info(
    query: UserInfoModel,
) -> Union[ResponseModel, tuple[ResponseModel, int]]:
    with app.db_session() as session:
        if query.id is not None:
            user = session.query(User).get(query.id)
        else:
            user = None
        if user is None and query.name is not None:
            user = session.query(User).filter(User.name == query.name).first()
        if user is None:
            return (
                ResponseModel(
                    status=StatusType.ERROR,
                    error='User does not exists',
                ),
                HTTPStatus.NOT_FOUND,
            )
        return ResponseModel(status=StatusType.OK, data=UserModel.from_orm(user))


@view_bp.route('/user/register', methods=['POST'])
@validate()
def user_register(
    body: UserRegisterModel,
) -> Union[ResponseModel, tuple[ResponseModel, int]]:
    try:
        with app.db_session() as session:
            new_user = User(name=body.name)
            session.add(new_user)
            session.flush()
            result_data = UserModel.from_orm(new_user)
            session.commit()
    except IntegrityError:
        return (
            ResponseModel(
                status=StatusType.ERROR,
                error='User already exists',
            ),
            HTTPStatus.BAD_REQUEST,
        )

    return ResponseModel(
        status=StatusType.OK,
        data=result_data,
    )


def has_new_exchange(session: Session, timestamp: int) -> bool:
    dt = datetime.utcfromtimestamp(timestamp)

    # whether we have CurrencyHistory that newer than given datetime/timestamp
    newer_history_count = (
        session.query(CurrencyHistory).filter(CurrencyHistory.datetime > dt).count()
    )
    return newer_history_count > 0


def buy(
    session: Session, user: User, currency: Currency, count: Decimal
) -> Union[ResponseModel, tuple[ResponseModel, int]]:
    currency_exchange = currency.get_buy_exchange(app.config['PERCENT_COMMISSION'])
    if user.balance < currency_exchange * count:
        return (
            ResponseModel(status=StatusType.ERROR, error='Not enough money on balance'),
            HTTPStatus.FORBIDDEN,
        )

    # noinspection PyTypeChecker
    for wallet in user.currency_wallets:
        if wallet.currency_id == currency.id:
            currency_wallet = wallet
            break
    else:
        currency_wallet = user.create_currency_wallet(currency)
        session.add(currency_wallet)

    wallet_operation = currency_wallet.create_operation(
        count, currency, TypeWalletOperation.BUY, app.config['PERCENT_COMMISSION']
    )
    session.add(wallet_operation)

    user.balance -= currency_exchange * count
    currency_wallet.balance += count

    return ResponseModel(
        status=StatusType.OK,
    )


def sell(
    session: Session, user: User, currency: Currency, count: Decimal
) -> Union[ResponseModel, tuple[ResponseModel, int]]:
    currency_exchange = currency.get_sell_exchange(app.config['PERCENT_COMMISSION'])
    currency_wallet = (
        session.query(CurrencyWallet)
        .join(User)
        .join(Currency)
        .filter(User.id == user.id, Currency.id == currency.id)
        .one_or_none()
    )

    if currency_wallet is None or currency_wallet.balance < count:
        return (
            ResponseModel(
                status=StatusType.ERROR,
                error='Not enough currency of this type',
            ),
            HTTPStatus.FORBIDDEN,
        )

    wallet_operation = currency_wallet.create_operation(
        count, currency, TypeWalletOperation.SELL, app.config['PERCENT_COMMISSION']
    )
    session.add(wallet_operation)

    user.balance += currency_exchange * count
    currency_wallet.balance -= count

    return ResponseModel(
        status=StatusType.OK,
    )


@view_bp.route('/currency/operation', methods=['POST'])
@validate()
def sell_buy_currency(
    body: OperationModel,
) -> Union[ResponseModel, tuple[ResponseModel, int]]:
    with app.db_session() as session:
        currency = (
            session.query(Currency)
            .filter(Currency.name == body.currency_name)
            .one_or_none()
        )

        if currency is None:
            return (
                ResponseModel(
                    status=StatusType.ERROR,
                    error='Unknown currency name',
                ),
                HTTPStatus.NOT_FOUND,
            )

        user = session.query(User).get(body.user_id)
        if user is None:
            return (
                ResponseModel(
                    status=StatusType.ERROR,
                    error='Unknown user id',
                ),
                HTTPStatus.NOT_FOUND,
            )

        if has_new_exchange(session, body.timestamp):
            return (
                ResponseModel(
                    status=StatusType.ERROR,
                    error='Currency exchange was changed',
                ),
                HTTPStatus.FORBIDDEN,
            )

        if body.operation is TypeWalletOperation.BUY:
            return buy(session, user, currency, body.count)
        return sell(session, user, currency, body.count)


@view_bp.route('/currency/get_info', methods=['GET'])
@validate()
def get_currency_info(
    query: CurrencyInfoModel,
) -> Union[ResponseModel, tuple[ResponseModel, int]]:
    with app.db_session() as session:
        currency = (
            session.query(Currency).filter(Currency.name == query.name).one_or_none()
        )

        if currency is None:
            return (
                ResponseModel(
                    status=StatusType.ERROR,
                    error='Unknown currency name',
                ),
                HTTPStatus.NOT_FOUND,
            )

        return ResponseModel(
            status=StatusType.OK,
            data=CurrencyModel.from_orm(currency),
        )


@view_bp.route('/currency/all', methods=['GET'])
@validate()
def get_all_currencies() -> ResponseModel:
    with app.db_session() as session:
        return ResponseModel(
            status=StatusType.OK,
            data=list(
                map(
                    CurrencyModel.from_orm,
                    session.query(Currency).order_by(Currency.id).all(),
                )
            ),
        )
