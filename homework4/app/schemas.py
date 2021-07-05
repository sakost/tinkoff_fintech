from datetime import datetime
from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel, Field, validator

from .models import TypeWalletOperation
from .utils import StatusType


class OperationModel(BaseModel):
    operation: TypeWalletOperation
    user_id: int
    currency_name: str = Field(max_length=3)
    count: Decimal = Field(gt=0)
    timestamp: int = Field(gt=0)

    @validator('currency_name')
    def upper_currency_name(cls, value: str) -> str:
        return value.upper()


class CurrencyInfoModel(BaseModel):
    name: str


class CurrencyModel(CurrencyInfoModel):
    id: int
    name: str
    exchange_rate: Decimal

    class Config:
        orm_mode = True


class UserInfoModel(BaseModel):
    id: Optional[int]
    name: Optional[str] = Field(min_length=3)


class UserRegisterModel(BaseModel):
    name: str = Field(min_length=3)


class WalletCurrencyHistoryModel(BaseModel):
    id: int
    exchange_rate: Decimal
    datetime: datetime
    percent_commission: Decimal

    class Config:
        orm_mode = True


class CurrencyWalletOperation(BaseModel):
    id: int
    currency_id: int
    currency_history_id: int
    type: TypeWalletOperation
    amount: Decimal

    currency_history: Optional[WalletCurrencyHistoryModel]

    class Config:
        orm_mode = True


class CurrencyWalletModel(BaseModel):
    currency_id: int
    balance: Decimal

    currency: Optional[CurrencyModel]
    operations: Optional[list[CurrencyWalletOperation]]

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    id: int
    name: str
    balance: Decimal
    reg_date: datetime
    currency_wallets: Optional[list[CurrencyWalletModel]]

    class Config:
        orm_mode = True


class ResponseModel(BaseModel):
    status: StatusType
    data: Optional[Union[UserModel, list[CurrencyModel], CurrencyModel]]
    error: Optional[str]
