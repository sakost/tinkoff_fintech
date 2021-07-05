from typing import Generator, Optional

from fastapi import Depends
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from .auth import security
from .config import get_settings
from .db import User, UserRole
from .db.session import get_session
from .exceptions import InternalError, InvalidCredentials


def get_db() -> Generator[Session, None, None]:
    db = get_session()()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), credentials: HTTPBasicCredentials = Depends(security)
) -> User:
    user: Optional[User] = (
        db.query(User).filter(User.name == credentials.username).first()
    )
    if not user:
        raise InvalidCredentials
    if not user.check_password(credentials.password):
        raise InvalidCredentials
    return user


def get_user_role(db: Session = Depends(get_db)) -> UserRole:
    role = (
        db.query(UserRole)
        .filter(UserRole.name == get_settings().USER_ROLE_NAME)
        .first()
    )

    if role is None:
        raise InternalError
    return role
