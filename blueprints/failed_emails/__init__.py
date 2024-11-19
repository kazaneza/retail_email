# blueprints/failed_emails/__init__.py

from flask import Blueprint

failed_emails_bp = Blueprint('failed_emails', __name__, template_folder='../../templates')

from . import routes
