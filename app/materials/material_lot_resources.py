from flask import request

from ..core.resources import (
    BaseDeleteResource,
    BaseGetResource,
    BasePatchResource,
    BasePostResource,
)
from .inventory_movement_services import InventoryMovementService
from .material_lot_schemas import inventory_movement_fields, material_lot_fields
from .material_lot_services import MaterialLotService


class MaterialLotGetResource(BaseGetResource):
    schema_get = staticmethod(MaterialLotService.get_obj)
    schema_list = staticmethod(
        lambda: MaterialLotService.get_obj_list(request.args.to_dict())
    )
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


class MaterialLotGetByMaterialResource(BaseGetResource):
    schema_get = staticmethod(MaterialLotService.get_lots_by_material)
    output_fields = material_lot_fields


# *************inventory movement services********************'
# *************** solo movimiento de materia prima****************
class InventoryMovementGetResource(BaseGetResource):
    schema_get = staticmethod(InventoryMovementService.get_obj)
    schema_list = staticmethod(
        lambda: InventoryMovementService.get_obj_list(request.args.to_dict())
    )
    output_fields = inventory_movement_fields


class InventoryMovementOutPostResource(BasePostResource):
    service_create = staticmethod(InventoryMovementService.create_obj_out)
    output_fields = inventory_movement_fields


class InventoryMovementTransferPostResource(BasePostResource):
    service_create = staticmethod(InventoryMovementService.create_obj_transfer)
    output_fields = inventory_movement_fields


class InventoryMovementAdjustPostResource(BasePostResource):
    service_create = staticmethod(InventoryMovementService.adjust_obj)
    output_fields = inventory_movement_fields
