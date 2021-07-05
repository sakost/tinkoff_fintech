from typing import Generator

from sqlalchemy.orm import Session

from .db.session import SessionLocal, engine


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal(bind=engine)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
