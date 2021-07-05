import sqlalchemy as sa

from .base_class import Base


class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(256), nullable=False, unique=True)

    books = sa.orm.relationship('Book', back_populates='owner', uselist=True)


class Book(Base):
    __tablename__ = 'books'

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(256), unique=True, nullable=False)
    text = sa.Column(sa.Text)

    owner_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    owner = sa.orm.relationship(User, back_populates='books', uselist=False)
