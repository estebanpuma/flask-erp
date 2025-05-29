from flask import request

from ..core.resources import BaseGetResource, BasePatchResource, BaseDeleteResource, BasePostResource, BulkUploadBaseResource

from .material_lot_services import MaterialLotService

from .material_lot_schemas import material_lot_fields, inventory_movement_fields
from .inventory_movement_services import InventoryMovementService



class MaterialLotGetResource(BaseGetResource):
    schema_get = staticmethod(MaterialLotService.get_obj)
    schema_list = staticmethod( lambda: MaterialLotService.get_obj_list(request.args.to_dict()))
    output_fields = material_lot_fields


class MaterialLotPostResource(BasePostResource):
    service_create = staticmethod(MaterialLotService.create_obj)
    output_fields = material_lot_fields


class MaterialLotPatchResource(BasePatchResource):
    service_get = staticmethod(MaterialLotService.get_obj)
    service_patch = staticmethod(MaterialLotService.patch_obj)
    output_fields = material_lot_fields


class MaterialLotDeleteResource(BaseDeleteResource):
    service_get = staticmethod(MaterialLotService.get_obj)
    service_delete = staticmethod(MaterialLotService.delete_obj)



#*************inventory movement services********************'
#*************** solo movimiento de materia prima****************
class InventoryMovementGetResource(BaseGetResource):
    schema_get = staticmethod(InventoryMovementService.get_obj)
    schema_list = staticmethod( lambda: InventoryMovementService.get_obj_list(request.args.to_dict()))
    output_fields = inventory_movement_fields


class InventoryMovementPostResource(BasePostResource):
    service_create = staticmethod(InventoryMovementService.create_obj)
    output_fields = inventory_movement_fields


class InventoryMovementAdjustResource(BasePostResource):
    service_create = staticmethod(InventoryMovementService.adjust_obj)
    output_fields = inventory_movement_fields



