from flask_restful import Resource, marshal_with, abort, request
from werkzeug.exceptions import HTTPException
from ..core.resources import BasePostResource, BasePatchResource, BaseDeleteResource, BaseGetResource, BasePutResource, BulkUploadBaseResource
from .services import CRMServices, ClientCategoryService, ProvinceService, CantonService, ClientBulkUploadService, ContactService
from .schemas import client_fields, province_fields, canton_fields, client_category_fields, contact_fields
from .validations import validate_client_data, validate_client_partial_data

from .models import Client

from flask_restful import Resource, reqparse



class ClientGetResource(BaseGetResource):
    """
    Devuelve un cliente o una lista de clientes 
    """
    schema_get = staticmethod(CRMServices.get_obj)       #servicio para obtener un elemento
    schema_list = staticmethod(lambda: CRMServices.get_obj_list(request.args.to_dict()))      #servicio para obtener una lista de elementos
    output_fields = client_fields


class ClientCreateResource(BasePostResource):
    """
    Crea un nuevo cliente en el sistema.
    """
    schema = staticmethod(validate_client_data)
    service_create = staticmethod(CRMServices.create_obj)
    output_fields = client_fields
           

class ClientPatchResource(BasePatchResource):
    """
    Actualiza algun campo o campos especificos del cliente
    """
    schema_validate_partial = staticmethod(validate_client_partial_data)   # Validaciones opcionales
    service_get = staticmethod(CRMServices.get_obj)
    service_patch = staticmethod(CRMServices.patch_obj)             # Servicio que hará la actualización parcial
    output_fields = client_fields            


class ClientDeleteResource(BaseDeleteResource):
    """
    Elimina un cliente (cuidado con las relaciones)
    """
    service_delete = staticmethod(CRMServices.delete_obj)


#***************************Client Bulk ********************************
#*********************************************************************
class ClientBulkUploadResource(BulkUploadBaseResource):
    import_service = ClientBulkUploadService
    row_handler = staticmethod(ClientBulkUploadService.handle_row)
    

#**************************ClientCategory**********************************
#*************************************************************************

class ClientCategoryGetResource(BaseGetResource):
    schema_get = staticmethod(ClientCategoryService.get_obj)
    schema_list = staticmethod(lambda: ClientCategoryService.get_obj_list(request.args.to_dict()))
    output_fields = client_category_fields

class ClientCategoryPostResource(BasePostResource):
    service_create = staticmethod(ClientCategoryService.create_obj)
    schema = None
    output_fields = client_category_fields


class ClientCategoryPatchResource(BasePatchResource):
    service_get = staticmethod(ClientCategoryService.get_obj)
    service_patch = staticmethod(ClientCategoryService.patch_obj)
    schema_validate_parcial = None
    output_fields = client_category_fields

class ClientCategoryDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(ClientCategoryService.delete_obj)


#****************************Location************************************
#**********************************************************************

class CantonGetResource(BaseGetResource):
    schema_get = staticmethod(CantonService.get_obj)
    schema_list = staticmethod(lambda: CantonService.get_obj_list(request.args.to_dict()))
    output_fields = canton_fields


class CantonPatchResource(BasePatchResource):
    schema_get = staticmethod(CantonService.get_obj)
    service_patch = staticmethod(CantonService.patch_obj)
    output_fields = canton_fields


class ProvinceGetResource(BaseGetResource):
    schema_get = staticmethod(ProvinceService.get_obj)
    schema_list = staticmethod(lambda: ProvinceService.get_obj_list(request.args.to_dict()))
    output_fields = province_fields

class ProvincePatchResource(BasePatchResource):
    service_get = staticmethod(ProvinceService.get_obj)
    service_patch = staticmethod(ProvinceService.patch_obj)
    output_fields = province_fields


#**************************Contacts***********************************
#***************************************************************

class ContactGetResource(BaseGetResource):
    schema_get = staticmethod(ContactService.get_obj)
    schema_list = staticmethod(lambda: ContactService.get_obj_list(request.args.to_dict()))
    output_fields = contact_fields

class ContactPostResource(BasePostResource):
    service_create = staticmethod(ContactService.create_obj)
    output_fields = contact_fields

class ContactPatchResource(BasePatchResource):
    service_get = staticmethod(ContactService.get_obj)
    service_patch = staticmethod(ContactService.patch_obj)
    output_fields = contact_fields

class ContactDeleteResource(BaseDeleteResource):
    service_get = staticmethod(ContactService.get_obj)
    service_delete = staticmethod(ContactService.delete_obj)