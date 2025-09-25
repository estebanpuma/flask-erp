from flask import request

from ..core.resources import (
    BaseDeleteResource,
    BaseGetResource,
    BasePatchResource,
    BasePostResource,
)
from .production_request_services import ProductionRequestServices
from .schemas import (
    op_fields,
    production_material_detail_fields,
    production_material_summary_fields,
    production_order_fields,
    production_order_line_fields,
    production_request_fields,
    production_resources_fields,
    variant_resource_usage,
)
from .services import (
    OperationService,
    ProductionMaterialService,
    ProductionOrderLineService,
    ProductionOrderService,
    ProductionResourceService,
    VariantResourceUsageService,
)


# ProductionRequests
class ProductionRequestGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionRequestServices.get_obj)
    schema_list = staticmethod(
        lambda: ProductionRequestServices.get_obj_list(request.args.to_dict())
    )
    output_fields = production_request_fields


# ProductionOrders
class ProductionOrderPostResource(BasePostResource):
    service_create = staticmethod(ProductionOrderService.create_obj)
    output_fields = production_order_fields


class ProductionOrderGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionOrderService.get_obj)
    schema_list = staticmethod(
        lambda: ProductionOrderService.get_obj_list(request.args.to_dict())
    )
    output_fields = production_order_fields


class ProductionOrderDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(ProductionOrderService.delete_obj)
    service_get = staticmethod(ProductionOrderService.get_obj)


# ProductionOrderLines
class ProductionLineGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionOrderLineService.get_obj)
    schema_list = staticmethod(
        lambda: ProductionOrderLineService.get_obj_list(request.args.to_dict())
    )
    output_fields = production_order_line_fields


class ProductionOrderLineGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionOrderLineService.get_obj_list_by_order)
    output_fields = production_order_line_fields


# ProductionOrderMaterials
class ProductionMaterialSummaryGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionMaterialService.get_material_summary)
    output_fields = production_material_summary_fields


class ProductionMaterialDetailsGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionMaterialService.get_line_materials)
    output_fields = production_material_detail_fields


# --------------------------------------------------------------------
# ----------------Operations
class OperationPostResource(BasePostResource):
    service_create = staticmethod(OperationService.create_obj)
    output_fields = op_fields


class OperationGetResource(BaseGetResource):
    schema_get = staticmethod(OperationService.get_obj)
    schema_list = staticmethod(
        lambda: OperationService.get_obj_list(request.args.to_dict())
    )
    output_fields = op_fields


class OperationPatchResource(BasePatchResource):
    service_get = staticmethod(OperationService.get_obj)
    service_patch = staticmethod(OperationService.patch_obj)
    output_fields = op_fields


class OperationDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(OperationService.delete_obj)
    service_get = staticmethod(OperationService.get_obj)


# ----------------ProductionResources
class ProductionResourcePostResource(BasePostResource):
    service_create = staticmethod(ProductionResourceService.create_obj)
    output_fields = production_resources_fields


class ProductionResourceGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionResourceService.get_obj)
    schema_list = staticmethod(
        lambda: ProductionResourceService.get_obj_list(request.args.to_dict())
    )
    output_fields = production_resources_fields


class ProductionResourcePatchResource(BasePatchResource):
    service_get = staticmethod(ProductionResourceService.get_obj)
    service_patch = staticmethod(ProductionResourceService.patch_obj)
    output_fields = production_resources_fields


class ProductionResourceDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(ProductionResourceService.delete_obj)
    service_get = staticmethod(ProductionResourceService.get_obj)


# ----------------VariantResourceUsage
class VariantUseResourcePostResource(BasePostResource):
    service_create = staticmethod(VariantResourceUsageService.create_obj)
    output_fields = variant_resource_usage


class VariantUseResourceGetResource(BaseGetResource):
    schema_get = staticmethod(VariantResourceUsageService.get_obj)
    schema_list = staticmethod(
        lambda: VariantResourceUsageService.get_obj_list(request.args.to_dict())
    )
    output_fields = variant_resource_usage


class VariantUseResourcePatchResource(BasePatchResource):
    service_get = staticmethod(VariantResourceUsageService.get_obj)
    service_patch = staticmethod(VariantResourceUsageService.patch_obj)
    output_fields = variant_resource_usage


"""


class ProductionReworkPostResource(BasePostResource):
    service_create = staticmethod(ProductionReworkService.create_obj)
    output_fields = production_rework_fields

class ProductionReworkGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionReworkService.get_obj)
    schema_list = staticmethod( lambda: ProductionReworkService.get_obj_list(request.args.to_dict()))
    output_fields = production_rework_fields



class ProductionCheckPointGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionCheckpointService.get_obj)
    schema_list = staticmethod( lambda: ProductionCheckpointService.get_obj_list(request.args.to_dict()))
    output_fields = production_checkpoint_fields


class ProductionCheckpointPostResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            order_line_id = data.get("order_line_id")
            stage = data.get("stage")
            if not order_line_id or not stage:
                return error_response("'order_line_id' y 'stage' son requeridos", 400)

            checkpoint = ProductionCheckpointService.complete_checkpoint(order_line_id, stage)
            return success_response(marshal(checkpoint, production_checkpoint_fields))
        except Exception as e:
            return error_response(f"Error al completar checkpoint: {str(e)}")

"""
