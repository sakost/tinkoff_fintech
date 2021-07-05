from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserGet(User):
    pass


class UserPost(UserBase):
    pass


class UserInDB(UserInDBBase):
    password_hash: str


class BookBase(BaseModel):
    title: str
    text: str


class BookCreate(BookBase):
    owner: User


class BookInDBBase(BookBase):
    class Config:
        orm_mode = True


class Book(BookInDBBase):
    pass
