"""
Profile Blueprint
Handles user profile viewing and editing
"""
from flask import Blueprint

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

from . import routes
