from flask import request

from ..core.resources import BaseGetResource, BasePatchResource, BaseDeleteResource, BasePostResource, BulkUploadBaseResource

from .material_lot_services import MaterialLotService

from .product_lot_schemas import product_lot_movement_fields, product_lot_fields
from .product_lot_services import ProductLotService, ProductLotMovementService



class ProductLotGetResource(BaseGetResource):
    schema_get = staticmethod(ProductLotService.get_obj)
    schema_list = staticmethod( lambda: ProductLotService.get_obj_list(request.args.to_dict()))
    output_fields = product_lot_fields


class ProductLotPostResource(BasePostResource):
    service_create = staticmethod(ProductLotService.create_obj)
    output_fields = product_lot_fields


class ProductLotPatchResource(BasePatchResource):
    service_get = staticmethod(ProductLotService.get_obj)
    service_patch = staticmethod(ProductLotService.patch_obj)
    output_fields = product_lot_fields


class ProductlLotDeleteResource(BaseDeleteResource):
    service_get = staticmethod(ProductLotService.get_obj)
    service_delete = staticmethod(ProductLotService.delete_obj)





#*****************ProductLotMovementsj************

class ProductLotAdjustPostResource(BasePostResource):
    service_create = staticmethod(ProductLotService.adjust_obj)
    output_fields = product_lot_movement_fields

class ProductLotMovementOutPostResource(BasePostResource):
    service_create = staticmethod(ProductLotMovementService.create_out_obj)
    output_fields = product_lot_movement_fields

class ProductLotMovementTransferPostResource(BasePostResource):
    service_create = staticmethod(ProductLotMovementService.create_transfer_obj)
    output_fields = product_lot_movement_fields

class ProductLotMovementGetResource(BaseGetResource):
    schema_get = staticmethod(ProductLotMovementService.get_obj)
    schema_list = staticmethod(lambda: ProductLotMovementService.get_obj_list(request.args.to_dict()))
    output_fields = product_lot_movement_fields

