from flask import request

from ..core.resources import (
    BaseDeleteResource,
    BaseGetResource,
    BasePatchResource,
    BasePostResource,
)
from .schemas import warehouse_fields
from .services import WarehouseService


class WarehouseGetResource(BaseGetResource):
    schema_get = staticmethod(WarehouseService.get_obj)
    schema_list = staticmethod(
        lambda: WarehouseService.get_obj_list(request.args.to_dict())
    )
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
