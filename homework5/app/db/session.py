from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import get_settings

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@lru_cache()
def get_engine() -> Engine:
    return create_engine(
        get_settings().SQLALCHEMY_DATABASE_URI,
        connect_args={
            'check_same_thread': False,
        },
    )


@lru_cache()
def get_session() -> sessionmaker:
    SessionLocal.configure(bind=get_engine())
    return SessionLocal


@contextmanager
def create_session() -> Iterator[Session]:
    session = get_session()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
