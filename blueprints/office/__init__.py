from flask import Blueprint

office_bp = Blueprint('office', __name__, url_prefix='/office')

from . import routes
