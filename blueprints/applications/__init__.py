"""
Applications Blueprint
Handles tevkil application management
"""
from flask import Blueprint

applications_bp = Blueprint('applications', __name__, url_prefix='/applications')

from . import routes
