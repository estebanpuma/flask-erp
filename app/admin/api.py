from flask import jsonify
from flask_restful import Api
from .resources import JobResource, RoleResource, UserResource
from . import admin_bp

admin_api = Api(admin_bp)



admin_api.add_resource(JobResource, '/api/v1/jobs', '/api/v1/jobs/<int:job_id>')

admin_api.add_resource(RoleResource, '/api/v1/roles', '/api/v1/roles/<int:role_id>')

admin_api.add_resource(UserResource, '/api/v1/users', '/api/v1/users/<int:user_id>')