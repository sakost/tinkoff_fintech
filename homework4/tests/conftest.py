# pylint: disable=redefined-outer-name
import os
import tempfile
from decimal import Decimal
from typing import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from app.app import create_app, init_db
from app.cli import create_db
from app.models import Base, Currency, User
from config import TestConfig


@pytest.fixture(scope='session', autouse=True)
def tests_setup_and_teardown() -> Iterator[None]:
    old_env = dict(os.environ)
    os.environ.update(dict(APP_SETTINGS='config.DevelopmentConfig'))
    yield
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture(scope='session')
def app() -> Iterator[Flask]:
    db_fd, database_file = tempfile.mkstemp()

    TestConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{database_file}'
    app = create_app(TestConfig)

    yield app

    os.close(db_fd)
    os.unlink(database_file)


@pytest.fixture(autouse=True)
def db_session(app: Flask) -> Iterator[Session]:
    with app.app_context():
        init_db(app)
        create_db()
        with app.db_session() as session:
            yield session
        Base.metadata.drop_all(bind=app.db_engine)


@pytest.fixture(scope='session')
def client(app: Flask) -> FlaskClient:  # type: ignore
    with app.test_client() as client:
        return client


@pytest.fixture(
    params=[
        User(id=1, name='user1', balance=Decimal(0)),
        User(id=2, name='user2', balance=Decimal(1000)),
        User(id=3, name='user3', balance=Decimal(3000)),
    ]
)
def user(request, db_session: Session) -> User:
    db_session.add(request.param)
    db_session.commit()
    return request.param


@pytest.fixture(
    params=[
        Currency(id=1, name='USD', exchange_rate=Decimal('1.0')),
        Currency(id=2, name='RUB', exchange_rate=Decimal('10.0')),
        Currency(id=3, name='EUR', exchange_rate=Decimal('0.1')),
        Currency(id=4, name='RUR', exchange_rate=Decimal('1000')),
    ]
)
def currency(request, db_session: Session) -> Currency:
    db_session.add(request.param)
    db_session.commit()
    return request.param
