from flask import Blueprint

rdi_bp = Blueprint('rdi', __name__, template_folder='templates')

from .models import *