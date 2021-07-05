from random import choices
from string import ascii_uppercase

import click
from flask import Flask, current_app
from flask.cli import with_appcontext

from app import bot
from app.models import Base, Currency


def fill_db(app: Flask) -> None:
    with app.db_session() as session:
        currencies = session.query(Currency).all()
        currency_names: list[str] = [str(currency.name) for currency in currencies]
        currency_chars = set(''.join(currency_names))
        allowed_chars = set(ascii_uppercase) - currency_chars
        currencies_count = len(currencies)
        if (currencies_count < app.config['DEFAULT_CURRENCIES_COUNT']) and app.config[
            'ADD_DEFAULT_CURRENCIES'
        ]:
            for _ in range(currencies_count, app.config['DEFAULT_CURRENCIES_COUNT']):
                allowed_chars_list = list(allowed_chars)
                currency = Currency(
                    name=''.join(choices(allowed_chars_list, k=3)),
                    exchange_rate=Currency.generate_exchange_rate(),
                )
                allowed_chars -= set(currency.name)  # type: ignore[arg-type]
                session.add(currency)


def create_db() -> None:
    app = current_app
    Base.metadata.create_all(bind=app.db_engine)
    fill_db(app)


@click.command('init_db')
@with_appcontext
def init_db_command() -> None:
    create_db()


@click.command('bot')
def bot_command() -> None:
    bot.main()
