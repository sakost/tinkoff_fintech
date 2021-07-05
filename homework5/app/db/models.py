import sqlalchemy as sa
from sqlalchemy_utils import generic_repr
from werkzeug.security import check_password_hash, generate_password_hash

from .base_class import Base


@generic_repr('name')
class UserRole(Base):
    __tablename__ = 'roles'

    id = sa.Column(sa.Integer, primary_key=True)

    name = sa.Column(sa.String(128), nullable=False)

    can_add_films = sa.Column(sa.Boolean, default=False, nullable=False)
    can_add_review = sa.Column(sa.Boolean, default=True, nullable=False)

    users = sa.orm.relationship('User', back_populates='role', uselist=True)


@generic_repr('id', 'name', 'role')
class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(256), nullable=False, unique=True)
    password_hash = sa.Column(sa.String(128), nullable=False)
    role_id = sa.Column(sa.Integer, sa.ForeignKey(UserRole.id))

    reviews = sa.orm.relationship('Review', back_populates='user', uselist=True)
    role = sa.orm.relationship(UserRole, back_populates='users', uselist=False)

    films = sa.orm.relationship('Film', back_populates='owner_user', uselist=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@generic_repr('id', 'name', 'owner_user')
class Film(Base):
    __tablename__ = 'films'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(128), nullable=False)
    released_year = sa.Column(sa.Integer, nullable=False)
    owner_user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False)

    avg_review_rate = sa.Column(sa.Float, nullable=True)
    count_reviews = sa.Column(sa.Integer, default=0, nullable=False)

    owner_user = sa.orm.relationship(User, back_populates='films', uselist=False)
    reviews = sa.orm.relationship('Review', back_populates='film', uselist=True)

    __table_args__ = (
        # first ever film was released at 1878 year
        sa.CheckConstraint('released_year >= 1878'),
    )


@generic_repr('id', 'film_id', 'user_id', 'score', 'film')
class Review(Base):
    __tablename__ = 'reviews'

    id = sa.Column(sa.Integer, primary_key=True)
    film_id = sa.Column(sa.Integer, sa.ForeignKey(Film.id))
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))

    score = sa.Column(sa.SmallInteger, nullable=False)
    text = sa.Column(sa.Text, nullable=True)

    film = sa.orm.relationship(Film, back_populates='reviews', uselist=False)
    user = sa.orm.relationship(User, back_populates='reviews', uselist=False)

    __table_args__ = (
        sa.CheckConstraint('0 <= score AND score <= 10'),
        sa.UniqueConstraint('film_id', 'user_id', name='_film_user_uc'),
    )
