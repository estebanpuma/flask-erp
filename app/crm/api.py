from flask import jsonify
from flask_restful import Api
from .resources import ClientResource, ClientSearchResource
from . import crm_bp

crm_api = Api(crm_bp)



crm_api.add_resource(ClientResource, '/api/v1/clients', '/api/v1/clients/<int:client_id>')

crm_api.add_resource(ClientSearchResource, '/api/v1/search/client')