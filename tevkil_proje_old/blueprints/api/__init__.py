"""
API Blueprint
Handles API endpoints for mobile, webhooks, and notifications.
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from blueprints.api import routes
