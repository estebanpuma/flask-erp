from flask_restful import request

from ..core.resources import BaseGetResource, BasePatchResource, BasePostResource
from .schemas import supplier_fields
from .services import SupplierService


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
