from sqlalchemy.engine import Engine

from .base_class import Base
from .session import engine


def init_db() -> Engine:
    Base.metadata.create_all(bind=engine)
    return engine
