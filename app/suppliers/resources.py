from flask_restful import request

from ..core.resources import BaseGetResource, BasePatchResource, BasePostResource
from .schemas import supplier_contact_fields, supplier_fields
from .services import SupplierContactService, SupplierService


class SupplierPostResource(BasePostResource):
    service_create = staticmethod(SupplierService.create_obj)
    output_fields = supplier_fields


class SupplierGetResource(BaseGetResource):
    schema_get = staticmethod(SupplierService.get_obj)
    schema_list = staticmethod(
        lambda: SupplierService.get_obj_list(request.args.to_dict())
    )
    output_fields = supplier_fields


class SupplierPatchResource(BasePatchResource):
    service_get = staticmethod(SupplierService.get_obj)
    service_patch = staticmethod(SupplierService.patch_obj)
    output_fields = supplier_fields


# ----------------------Contact--------------------
class SupplierContactPostResource(BasePostResource):
    service_create = staticmethod(SupplierContactService.create_obj)
    output_fields = supplier_contact_fields


class SupplierContactGetResource(BaseGetResource):
    schema_get = staticmethod(SupplierContactService.get_obj)
    schema_list = staticmethod(
        lambda: SupplierContactService.get_obj_list(request.args.to_dict())
    )
    output_fields = supplier_contact_fields


class SupplierContactGetListResource(BaseGetResource):
    schema_get = staticmethod(SupplierContactService.get_obj_list_by_client)
    output_fields = supplier_contact_fields


class SupplierContactPatchResource(BasePatchResource):
    service_get = staticmethod(SupplierContactService.get_obj)
    service_patch = staticmethod(SupplierContactService.patch_obj)
    output_fields = supplier_contact_fields
