from flask import Blueprint
from flask_restful import Api
from .resources import JobResource, RoleResource, UserGetResource


admin_api_bp = Blueprint('admin', __name__, url_prefix='/api/v1')
admin_api = Api(admin_api_bp)


