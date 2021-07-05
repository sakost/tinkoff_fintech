# pylint: disable=redefined-outer-name
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import app
from app.db.base_class import Base
from app.db.models import Book, User
from app.db.session import SessionLocal
from app.db.init_db import init_db


@pytest.fixture(scope='session')
def client():
    test_client = TestClient(app.app)
    return test_client


@pytest.fixture()
def _init_db():
    engine = init_db()

    with SessionLocal(bind=engine) as local_session:
        yield local_session

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def db_session(_init_db):
    return _init_db


@pytest.fixture()
def user(db_session: Session) -> User:
    user = User(name='user')
    db_session.add(user)
    db_session.commit()

    user = db_session.query(User).filter_by(name='user').one()
    return user


@pytest.fixture()
def book(user: User, db_session: Session) -> Book:
    book = Book(title='book title', text='some text', owner=user)
    db_session.add(book)
    db_session.commit()

    book = db_session.query(Book).filter_by(title='book title').one()
    return book
