from flask_restful import Api
from flask import Blueprint
from app.core.resources import HealthCheckResource

core_api_bp = Blueprint('core_api', __name__, url_prefix='/api/v1')

api = Api(core_api_bp)

api.add_resource(HealthCheckResource, '/health')

