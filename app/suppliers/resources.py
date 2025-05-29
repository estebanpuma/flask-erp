from flask_restful import Resource, request, marshal_with, marshal_with_field, marshal

from ..core.resources import BaseGetResource, BasePostResource, BasePatchResource, BaseDeleteResource

from .services import SupplierService

from .schemas import supplier_fields

from ..core.utils import *
from ..core.exceptions import AppError


class SupplierPostResource(BasePostResource):
    service_create = staticmethod(SupplierService.create_obj)
    output_fields = supplier_fields

class SupplierGetResource(BaseGetResource):
    schema_get = staticmethod(SupplierService.get_obj)
    schema_list = staticmethod(lambda: SupplierService.get_obj_list(request.args.to_dict()))
    output_fields = supplier_fields

class SupplierPatchResource(BasePatchResource):
    service_get = staticmethod(SupplierService.get_obj)
    service_patch = staticmethod(SupplierService.patch_obj)
    output_fields = supplier_fields
