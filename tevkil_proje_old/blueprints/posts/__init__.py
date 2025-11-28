"""
Posts Blueprint
Handles tevkil post listing, creation, editing, viewing, and applications.
"""

from flask import Blueprint

posts_bp = Blueprint('posts', __name__)

from blueprints.posts import routes
