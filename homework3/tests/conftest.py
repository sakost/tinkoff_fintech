# pylint: disable=redefined-outer-name
import os
import tempfile

import pytest

from config import TestConfig
from todo_list.app import create_app, db


@pytest.fixture(scope='session')
def app():
    db_fd, database_file = tempfile.mkstemp()

    TestConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{database_file}'
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(database_file)


@pytest.fixture(scope='session')
def _db(app):
    with app.app_context():
        yield db


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()
