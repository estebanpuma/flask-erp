from flask import Blueprint

finance_bp = Blueprint('finance', __name__, template_folder='templates')

from . import routes, api