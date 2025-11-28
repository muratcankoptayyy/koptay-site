"""
Chat Blueprint
Handles real-time messaging and conversations.
"""

from flask import Blueprint

chat_bp = Blueprint('chat', __name__)

from blueprints.chat import routes
