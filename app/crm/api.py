
from flask_restful import Api

from flask import Blueprint


from .resources import (ClientGetResource, 
                        ClientCreateResource, 
                        ClientPatchResource, 
                        ClientDeleteResource, 
                        ClientBulkUploadResource,
                        ClientSearchResource,
                        )
from .resources import ClientCategoryDeleteResource, ClientCategoryGetResource, ClientCategoryPatchResource, ClientCategoryPostResource
from .resources import CantonGetResource, CantonPatchResource, ProvinceGetResource, ProvincePatchResource
from .resources import ContactDeleteResource, ContactGetResource, ContactPatchResource, ContactPostResource

crm_api_bp = Blueprint('crm_api', __name__, url_prefix='/api/v1')

crm_api = Api(crm_api_bp)


#************************CLients*************************************************
crm_api.add_resource(ClientCreateResource, '/clients')
crm_api.add_resource(ClientGetResource, '/clients', '/clients/<int:resource_id>')
crm_api.add_resource(ClientPatchResource, '/clients/<int:resource_id>')
crm_api.add_resource(ClientDeleteResource, '/clients/<int:resource_id>')

crm_api.add_resource(ClientSearchResource, '/clients/search')

#bulkupload
crm_api.add_resource(ClientBulkUploadResource, '/clients/upload-excel')


#********************************CLientsCategory*************************************
#////******************************************************************************

crm_api.add_resource(ClientCategoryGetResource, "/client-category", "/client-category/<int:resource_id>")
crm_api.add_resource(ClientCategoryPostResource, "/client-category")
crm_api.add_resource(ClientCategoryPatchResource, "/client-category/<int:resource_id>")
crm_api.add_resource(ClientCategoryDeleteResource, "/client-category/<int:resource_id>")


#/*********************************Location***********************************
#*******************************************************************************


crm_api.add_resource(CantonGetResource, "/cantons", "/cantons/<int:resource_id>")
crm_api.add_resource(CantonPatchResource, "/cantons/<int:resource_id>")

crm_api.add_resource(ProvinceGetResource, "/provinces", "/provinces/<int:resource_id>")
crm_api.add_resource(ProvincePatchResource, "/provinces/<int:resource_id>")


#*********************************COntacts*************************************
#************************************************************************************

crm_api.add_resource(ContactGetResource, "/contacts", "/contacts/<int:resource_id>")
crm_api.add_resource(ContactPostResource, "/contacts")
crm_api.add_resource(ContactPatchResource, "/contacts/<int:resource_id>")
crm_api.add_resource(ContactDeleteResource, "/contacts/<int:resource_id>")