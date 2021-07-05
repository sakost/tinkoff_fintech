import os
from typing import Optional, Type

from flask import Flask, current_app

from config import BaseConfig

from . import cli
from .currency_checker import CurrencyChecker
from .database import init_db
from .views import view_bp


def start_currency_checker() -> None:
    current_app.currency_checker = CurrencyChecker(
        current_app.config['WORKER_SLEEP_TIME'],
        (
            current_app.config['PERCENT_MINIMUM_CHANGE'],
            current_app.config['PERCENT_MAXIMUM_CHANGE'],
        ),
        current_app.db_session,
    )
    current_app.currency_checker.start()


def create_app(config: Optional[Type[BaseConfig]] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    if config is not None:
        app.config.from_object(config)
    else:
        app.config.from_object(os.environ.get('APP_SETTINGS', BaseConfig))

    init_db(app)

    app.before_first_request_funcs.append(start_currency_checker)

    app.register_blueprint(view_bp)

    app.cli.add_command(cli.init_db_command)
    app.cli.add_command(cli.bot_command)

    return app
