from contextlib import contextmanager
from typing import Any, Generator

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

session_factory = sessionmaker()
Session = scoped_session(session_factory)


@contextmanager
def create_session() -> Generator[scoped_session, None, None]:
    new_session = Session()

    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


def init_db(app: Flask, **engine_kwargs: Any) -> Flask:
    app.db_engine = create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'], **engine_kwargs
    )
    app.db_session = create_session
    Session.configure(bind=app.db_engine, expire_on_commit=False)

    return app
