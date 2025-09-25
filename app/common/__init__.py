from flask import Blueprint

from .models import AppSetting as AppSetting
from .models import BaseModel as BaseModel
from .models import SoftDeleteMixin as SoftDeleteMixin

common_bp = Blueprint("common", __name__)
