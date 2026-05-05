from flask import Blueprint
from flask_restful import Api

from .resources import SecuenceResource

common_api_bp = Blueprint("common_api", __name__, url_prefix="/api/v1")

common_api = Api(common_api_bp)

common_api.add_resource(SecuenceResource, "/secuence-generator")
