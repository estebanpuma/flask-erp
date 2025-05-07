# app/auth/api.py
from flask import Blueprint
from flask_restful import Api
from .resources import AuthLoginResource #AuthRefreshResource  # veremos refresh abajo

auth_bp = Blueprint("auth_api", __name__, url_prefix="/api/v1/auth")
auth_api = Api(auth_bp)

auth_api.add_resource(AuthLoginResource,   "/login")
#auth_api.add_resource(AuthRefreshResource, "/refresh")  # opcional


