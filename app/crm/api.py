from flask import jsonify
from flask_restful import Api
from .resources import ClientResource, ClientSearchResource, ProvinceResource, CantonResource
from . import crm_bp

crm_api = Api(crm_bp)

crm_api.add_resource(CantonResource, '/api/v1/cantons', '/api/v1/cantons/<int:canton_id>')

crm_api.add_resource(ProvinceResource, '/api/v1/provinces', '/api/v1/provinces/<int:province_id>')

crm_api.add_resource(ClientResource, '/api/v1/clients', '/api/v1/clients/<int:client_id>')

crm_api.add_resource(ClientSearchResource, '/api/v1/search/client')