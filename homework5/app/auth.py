from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .db import User, create_session
from .exceptions import InvalidCredentials

security = HTTPBasic()


def auth_required(credentials: HTTPBasicCredentials = Depends(security)) -> User:
    with create_session() as session:
        user = session.query(User).filter_by(name=credentials.username).one_or_none()
        if user is None:
            raise InvalidCredentials

        if not user.check_password(credentials.password):
            raise InvalidCredentials

        return user
