from flask_restful import Resource, marshal, request

from ..core.resources import (
    BaseDeleteResource,
    BaseGetResource,
    BasePatchResource,
    BasePostResource,
    BulkUploadBaseResource,
)
from ..core.utils import success_response
from .schemas import (
    canton_fields,
    client_category_fields,
    client_fields,
    client_image_fields,
    client_search_fields,
    contact_fields,
    province_fields,
)
from .services import (
    CantonService,
    ClientBulkUploadService,
    ClientCategoryService,
    ClientImageService,
    ContactService,
    CRMServices,
    ProvinceService,
)
from .validations import validate_client_data


class ClientGetResource(BaseGetResource):
    """
    Devuelve un cliente o una lista de clientes
    """

    schema_get = staticmethod(CRMServices.get_obj)  # servicio para obtener un elemento
    schema_list = staticmethod(
        lambda: CRMServices.get_obj_list(request.args.to_dict())
    )  # servicio para obtener una lista de elementos
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

    service_get = staticmethod(CRMServices.get_obj)
    service_patch = staticmethod(
        CRMServices.patch_obj
    )  # Servicio que hará la actualización parcial
    output_fields = client_fields


class ClientDeleteResource(BaseDeleteResource):
    """
    Elimina un cliente (cuidado con las relaciones)
    """

    service_delete = staticmethod(CRMServices.delete_obj)


class ClientSearchResource(Resource):
    def get(self):
        args = request.args.to_dict()

        results = CRMServices.search_clients(query=args["q"])
        if results:
            return success_response(marshal(results, client_search_fields), 200)


# ------------------------Client Images-------------------------------
class ClientImageGetResource(Resource):
    def get(self, resource_id):
        images = ClientImageService.get_obj_list(resource_id)
        return success_response(marshal(images, client_image_fields), 200)


class ClientImagePostResource(BasePostResource):
    service_create = staticmethod(ClientImageService.create_obj)
    output_fields = client_image_fields


class ClientImageDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(ClientImageService.delete_obj)


# ***************************Client Bulk ********************************
# *********************************************************************
class ClientBulkUploadResource(BulkUploadBaseResource):
    import_service = ClientBulkUploadService
    row_handler = staticmethod(ClientBulkUploadService.handle_row)


# **************************ClientCategory**********************************
# *************************************************************************


class ClientCategoryGetResource(BaseGetResource):
    schema_get = staticmethod(ClientCategoryService.get_obj)
    schema_list = staticmethod(
        lambda: ClientCategoryService.get_obj_list(request.args.to_dict())
    )
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


# ****************************Location************************************
# **********************************************************************


class CantonGetResource(BaseGetResource):
    schema_get = staticmethod(CantonService.get_obj)
    schema_list = staticmethod(
        lambda: CantonService.get_obj_list(request.args.to_dict())
    )
    output_fields = canton_fields


class CantonPatchResource(BasePatchResource):
    schema_get = staticmethod(CantonService.get_obj)
    service_patch = staticmethod(CantonService.patch_obj)
    output_fields = canton_fields


class ProvinceGetResource(BaseGetResource):
    schema_get = staticmethod(ProvinceService.get_obj)
    schema_list = staticmethod(
        lambda: ProvinceService.get_obj_list(request.args.to_dict())
    )
    output_fields = province_fields


class ProvincePatchResource(BasePatchResource):
    service_get = staticmethod(ProvinceService.get_obj)
    service_patch = staticmethod(ProvinceService.patch_obj)
    output_fields = province_fields


# **************************Contacts***********************************
# ***************************************************************


class ContactGetResource(BaseGetResource):
    schema_get = staticmethod(ContactService.get_obj)
    schema_list = staticmethod(
        lambda: ContactService.get_obj_list(request.args.to_dict())
    )
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
