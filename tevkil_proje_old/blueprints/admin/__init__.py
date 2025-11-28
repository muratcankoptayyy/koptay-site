"""
Admin Blueprint
Handles admin panel, analytics, user management, and reports.
"""

from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from blueprints.admin import routes
