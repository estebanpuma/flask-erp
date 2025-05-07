
from flask_restful import Api

from flask import Blueprint

from .resources import ClientSearchResource, ProvinceResource, CantonResource
from .resources import ClientGetResource, ClientCreateResource, ClientPatchResource
from .resources import ClientDeleteResource

crm_api_bp = Blueprint('crm_api', __name__, url_prefix='/api/v1')

crm_api = Api(crm_api_bp)


crm_api.add_resource(CantonResource, '/cantons', '/cantons/<int:canton_id>')

crm_api.add_resource(ProvinceResource, '/provinces', '/provinces/<int:province_id>')

crm_api.add_resource(ClientCreateResource, '/clients')

crm_api.add_resource(ClientSearchResource,  '/clients/search/client')

crm_api.add_resource(ClientGetResource, '/clients', '/clients/<int:resource_id>')

crm_api.add_resource(ClientPatchResource, '/clients/<int:resource_id>')

crm_api.add_resource(ClientDeleteResource, '/clients/<int:resource_id>')