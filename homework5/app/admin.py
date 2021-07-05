from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from .db.models import Film, Review, User, UserRole
from .db.session import get_session


def create_app() -> Flask:  # pragma: no cover
    app = Flask(__name__)
    admin = Admin(app)
    add_models(admin)

    return app


def add_models(admin: Admin) -> None:  # pragma: no cover
    session = get_session()()
    admin.add_view(ModelView(User, session))
    admin.add_view(ModelView(Film, session))
    admin.add_view(ModelView(Review, session))
    admin.add_view(ModelView(UserRole, session))


if __name__ == '__main__':  # pragma: no cover
    create_app().run()
