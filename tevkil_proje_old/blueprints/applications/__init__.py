"""
Applications Blueprint
Handles application management (received, sent, accept, reject).
"""

from flask import Blueprint

applications_bp = Blueprint('applications', __name__)

from blueprints.applications import routes
