from flask import Blueprint

from .utils import FlashMessageCategory

jinja_extensions_bp = Blueprint('jinja_extensions', __name__)


@jinja_extensions_bp.app_template_global()
def flash_message_categories():
    return FlashMessageCategory
