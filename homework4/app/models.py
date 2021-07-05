import random
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import generic_repr

if TYPE_CHECKING:  # pragma: no cover
    from typing import Type, TypeVar

    from sqlalchemy.sql.type_api import TypeEngine  # pylint: disable=ungrouped-imports

    T = TypeVar('T')

    class SaEnum(TypeEngine[T]):  # pylint: disable=unsubscriptable-object
        def __init__(self, enum: Type[T]) -> None:  # pylint: disable=unused-argument
            ...


else:
    from sqlalchemy import Enum as SaEnum  # pylint: disable=ungrouped-imports

Base = declarative_base()


class TypeWalletOperation(Enum):
    BUY = 'buy'
    SELL = 'sell'


@generic_repr
class Currency(Base):
    __tablename__ = 'currencies'

    id = sa.Column(sa.Integer, primary_key=True)  # type: ignore
    name = sa.Column(sa.String(3), unique=True, nullable=False)
    exchange_rate = sa.Column(sa.Numeric(38, 10), nullable=False)

    wallet_operations = relationship('WalletOperation', backref='currency_type')

    __table_args__ = (sa.CheckConstraint('exchange_rate > 0'),)

    MIN_RANDOM_EXCHANGE = 1
    MAX_RANDOM_EXCHANGE = 100
    RANDOM_EXCHANGE_EXPONENT = 0

    @classmethod
    def generate_exchange_rate(cls) -> Decimal:
        return (
            Decimal(random.randint(cls.MIN_RANDOM_EXCHANGE, cls.MAX_RANDOM_EXCHANGE))
            / Decimal('1' + '0' * cls.RANDOM_EXCHANGE_EXPONENT).normalize()
        )

    def get_buy_exchange(self, percent: Decimal) -> Decimal:
        return self.exchange_rate * Decimal(1 + percent)

    def get_sell_exchange(self, percent: Decimal) -> Decimal:
        return self.exchange_rate * Decimal(1 - percent)


@generic_repr
class CurrencyHistory(Base):
    __tablename__ = 'currencies_history'

    id = sa.Column(sa.Integer, primary_key=True)  # type: ignore
    currency_id = sa.Column(sa.Integer, sa.ForeignKey(Currency.id))
    exchange_rate = sa.Column(sa.DECIMAL(38, 10), nullable=False)
    datetime = sa.Column(sa.DateTime(), default=datetime.utcnow)

    __table_args__ = (sa.CheckConstraint('exchange_rate > 0'),)


@generic_repr
class WalletCurrencyHistory(Base):
    __tablename__ = 'wallet_currencies_history'

    id = sa.Column(sa.Integer, primary_key=True)  # type: ignore
    exchange_rate = sa.Column(sa.DECIMAL(38, 10), nullable=False)
    datetime = sa.Column(sa.DateTime(), default=datetime.utcnow)
    percent_commission = sa.Column(sa.Numeric(38, 10), nullable=False)

    __table_args__ = (sa.CheckConstraint('exchange_rate > 0'),)


@generic_repr
class WalletOperation(Base):
    __tablename__ = 'wallet_operations'

    id = sa.Column(sa.Integer, primary_key=True)  # type: ignore
    currency_id = sa.Column(sa.Integer, sa.ForeignKey(Currency.id))
    wallet_id = sa.Column(sa.Integer, sa.ForeignKey('currency_wallets.id'))
    currency_history_id = sa.Column(sa.Integer, sa.ForeignKey(WalletCurrencyHistory.id))
    type = sa.Column(SaEnum(TypeWalletOperation), nullable=False)
    amount = sa.Column(sa.Numeric(38, 10), nullable=False)

    currency_history = relationship(
        WalletCurrencyHistory, backref='operations', uselist=False
    )
    wallet = relationship('CurrencyWallet', back_populates='operations', uselist=False)


@generic_repr
class CurrencyWallet(
    Base,
):
    __tablename__ = 'currency_wallets'
    __table_args__ = (sa.CheckConstraint('balance >= 0'),)

    id = sa.Column(sa.Integer, primary_key=True)  # type: ignore
    balance = sa.Column(sa.Numeric(38, 10), nullable=False, default=0)
    currency_id = sa.Column(sa.Integer, sa.ForeignKey(Currency.id))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))

    currency = relationship(Currency, uselist=False)
    operations = relationship(
        WalletOperation,
        back_populates='wallet',
        uselist=True,
    )

    def create_operation(
        self,
        amount: Decimal,
        currency: Currency,
        op_type: TypeWalletOperation,
        percent_commission: Decimal,
    ) -> WalletOperation:
        return WalletOperation(
            currency_id=currency.id,
            wallet=self,
            currency_history=WalletCurrencyHistory(
                exchange_rate=currency.exchange_rate,
                percent_commission=percent_commission,
            ),
            amount=amount,
            type=op_type,
        )


@generic_repr
class User(
    Base,
):
    __tablename__ = 'users'
    __table_args__ = (sa.CheckConstraint('balance >= 0'),)

    id = sa.Column(sa.Integer, primary_key=True)  # type: ignore
    name = sa.Column(sa.String(256), unique=True, nullable=False)
    balance = sa.Column(sa.Numeric(38, 10), default=1000, nullable=False)
    reg_date = sa.Column(sa.DateTime(), default=datetime.utcnow, nullable=False)

    currency_wallets = relationship(
        CurrencyWallet,
        backref='user',
        uselist=True,
    )

    def create_currency_wallet(self, currency: Currency) -> CurrencyWallet:
        return CurrencyWallet(user_id=self.id, currency=currency, balance=Decimal(0))

    def format_reg_date(self, format_: str) -> str:
        return self.reg_date.strftime(format_)
