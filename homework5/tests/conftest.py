# pylint: disable=redefined-outer-name
import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import app, config
from app.db import Base, Film, Review, User, UserRole, create_session
from app.db.init_db import init_db
from app.db.session import get_engine


def get_settings_override(db_file: str) -> config.Settings:
    return config.get_settings(
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_file}', _env_file='tests.env'
    )


@pytest.fixture(scope='session')
def client():
    test_client = TestClient(app.app)
    return test_client


@pytest.fixture(autouse=True)
def _init_db():
    db_fd, db_file = tempfile.mkstemp()
    get_settings_override(db_file)
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    with create_session() as local_session:
        init_db(local_session)
        yield local_session

    Base.metadata.drop_all(bind=engine)

    os.unlink(db_file)
    os.close(db_fd)


@pytest.fixture()
def db_session(_init_db):
    return _init_db


@pytest.fixture()
def user(db_session: Session) -> User:
    user = User(name='user', role=db_session.query(UserRole).filter_by(id=2).one())
    user.set_password('password')
    db_session.add(user)
    db_session.commit()

    user = db_session.query(User).filter_by(name='user').one()
    return user


@pytest.fixture()
def admin(db_session: Session) -> User:
    user: User = db_session.query(User).get(1)  # type: ignore
    return user


@pytest.fixture()
def film(db_session: Session, admin: User) -> Film:
    film = Film(name='film', released_year=2000, owner_user=admin)
    db_session.add(film)
    db_session.flush()
    film_id = film.id
    db_session.commit()

    return db_session.query(Film).get(film_id)  # type: ignore


@pytest.fixture()
def review(db_session: Session, admin: User, film: Film) -> Review:
    review = Review(film=film, user=admin, score=5, text='text')
    db_session.add(review)
    db_session.flush()
    review_id = review.id
    db_session.commit()

    return db_session.query(Review).get(review_id)  # type: ignore
