from flask import Flask
from sqlalchemy.orm import Session

from app.cli import fill_db
from app.models import Currency


def test_fill_db(app: Flask, db_session: Session):
    old_add_default_currencies = app.config['ADD_DEFAULT_CURRENCIES']
    app.config['ADD_DEFAULT_CURRENCIES'] = True
    fill_db(app)

    assert len(db_session.query(Currency).all()) == 5
    app.config['ADD_DEFAULT_CURRENCIES'] = old_add_default_currencies
