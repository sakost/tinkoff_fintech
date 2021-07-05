from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import Base, User, UserRole
from app.db.session import get_engine


def init_db(session: Session) -> None:
    Base.metadata.create_all(bind=get_engine())

    super_user = (
        session.query(User).filter_by(name=get_settings().FIRST_SUPERUSER).first()
    )
    super_user_role = (
        session.query(UserRole)
        .filter_by(name=get_settings().FIRST_SUPERUSER_ROLE)
        .first()
    )
    user_role = (
        session.query(UserRole).filter_by(name=get_settings().USER_ROLE_NAME).first()
    )

    if not super_user_role:
        super_user_role = UserRole(
            name=get_settings().FIRST_SUPERUSER_ROLE,
            can_add_films=True,
            can_add_review=True,
        )
        session.add(super_user_role)

    if not user_role:
        user_role = UserRole(
            name=get_settings().USER_ROLE_NAME,
        )
        session.add(user_role)

    if not super_user:
        super_user = User(
            name=get_settings().FIRST_SUPERUSER,
            role=super_user_role,
        )
        super_user.set_password(get_settings().FIRST_SUPERUSER_PASSWORD)
        session.add(super_user)

    session.commit()
