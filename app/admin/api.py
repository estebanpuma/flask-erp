from flask import jsonify
from flask_restful import Api
from .resources import JobResource, RoleResource, UserGetResource
from . import admin_bp

admin_api = Api(admin_bp)



admin_api.add_resource(JobResource, '/api/v1/jobs', '/api/v1/jobs/<int:job_id>')

admin_api.add_resource(RoleResource, '/api/v1/roles', '/api/v1/roles/<int:role_id>')

admin_api.add_resource(UserGetResource, '/api/v1/users', '/api/v1/users/<int:resource_id>')