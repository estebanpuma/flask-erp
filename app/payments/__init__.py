from flask import Blueprint

payments_bp = Blueprint('payments', __name__, template_folder='templates')

from . import routes, api

from .models import *