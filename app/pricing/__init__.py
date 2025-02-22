from flask import Blueprint

pricing_bp = Blueprint('pricing', __name__, template_folder='templates')

from . import routes, api