import os
from typing import Optional, Type

from flask import Flask

from config import BaseConfig

from .database_extensions import database_extensions_bp
from .jinja_extensions import jinja_extensions_bp
from .models import db
from .views import view_bp


def create_app(config: Optional[Type[BaseConfig]] = None):
    app = Flask(__name__, instance_relative_config=True)

    if config is not None:
        app.config.from_object(config)
    else:
        app.config.from_object(os.environ.get('APP_SETTINGS', BaseConfig))

    db.init_app(app)

    app.register_blueprint(view_bp)
    app.register_blueprint(database_extensions_bp)
    app.register_blueprint(jinja_extensions_bp)

    return app
