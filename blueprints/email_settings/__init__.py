# blueprints/email_settings/__init__.py

from flask import Blueprint

email_settings_bp = Blueprint('email_settings', __name__, template_folder='../../templates')

from . import routes
