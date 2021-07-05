from flask import Blueprint
from flask import current_app as app

from .models import db

database_extensions_bp = Blueprint('database_extensions', __name__)


@database_extensions_bp.before_app_first_request
def create_models():
    app.logger.debug('database will be created now')
    db.create_all()
    app.logger.info('database was created')
