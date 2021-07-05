from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import models
from .deps import get_db
from .exceptions import BookAlreadyExists, UserAlreadyExists, UserNotFound
from .schemas import Book, BookCreate, UserCreate, UserGet

router = APIRouter()


@router.get('/{user_id}/books')
def get_books(user_id: int, db: Session = Depends(get_db)) -> list[Book]:
    user: Optional[models.User] = (
        db.query(models.User).filter(models.User.id == user_id).one_or_none()
    )
    if not user:
        raise UserNotFound

    return list(map(Book.from_orm, user.books))


@router.post('/{user_id}/books')
def add_book(
    user_id: int, book: BookCreate, db: Session = Depends(get_db)
) -> dict[str, str]:
    user: Optional[models.User] = (
        db.query(models.User).filter(models.User.id == user_id).one_or_none()
    )
    if not user:
        raise UserNotFound

    db_book = models.Book(title=book.title, text=book.text, owner=user)
    db.add(db_book)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BookAlreadyExists  # pylint: disable=raise-missing-from

    return {'status': 'ok'}


@router.post('/user')
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> dict[str, str]:
    db_user = models.User(name=user.name)
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        raise UserAlreadyExists  # pylint: disable=raise-missing-from
    return {'status': 'ok'}


@router.get('/user/{user_id}')
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserGet:
    db_user: Optional[models.User] = (
        db.query(models.User).filter(models.User.id == user_id).one_or_none()
    )
    if not db_user:
        raise UserNotFound
    return UserGet.from_orm(db_user)
