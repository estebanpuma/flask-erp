from flask import request
from flask_restful import Resource, marshal, marshal_with
from ..core.resources import BasePatchResource, BaseGetResource, BaseDeleteResource, BasePostResource
from .services import WarehouseService
from .schemas import warehouse_fields


class WarehouseGetResource(BaseGetResource):
    schema_get = staticmethod(WarehouseService.get_obj)
    schema_list = staticmethod( lambda: WarehouseService.get_obj_list(request.args.to_dict()))
    output_fields = warehouse_fields


class WarehousePostResource(BasePostResource):
    service_create = staticmethod(WarehouseService.create_obj)
    output_fields = warehouse_fields


class WarehousePatchResource(BasePatchResource):
    service_get = staticmethod(WarehouseService.get_obj)
    service_patch = staticmethod(WarehouseService.patch_obj)
    output_fields = warehouse_fields
        


class WarehouseDeleteResource(BaseDeleteResource):
    service_get = staticmethod(WarehouseService.get_obj)
    service_delete = staticmethod(WarehouseService.delete_obj)
    
