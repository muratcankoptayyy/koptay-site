"""
Messages Blueprint
Handles messaging between users
"""
from flask import Blueprint

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')

from . import routes
