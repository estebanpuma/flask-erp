from flask import Blueprint

materials_bp = Blueprint('materials', __name__, template_folder='templates')

from . import routes, api

from .models import *

