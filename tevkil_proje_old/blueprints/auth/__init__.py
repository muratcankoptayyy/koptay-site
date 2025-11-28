"""
Authentication Blueprint
Handles user registration, login, logout, password reset, and 2FA.
"""

from flask import Blueprint

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Import routes after blueprint creation to avoid circular imports
from blueprints.auth import routes
