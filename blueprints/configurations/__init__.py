# blueprints/configurations/__init__.py

from flask import Blueprint

configurations_bp = Blueprint('configurations', __name__, template_folder='../../templates')

from . import routes
