from flask import request, jsonify, current_app

from flask_restful import Resource, marshal_with, abort, marshal

from sqlalchemy.exc import SQLAlchemyError

from .services import (
    ProductionOrderService,
)

from .production_request_services import ProductionRequestServices

from .schemas import (
    production_checkpoint_fields, 
    production_material_detail_fields,
    production_material_detail_for_rework_fields,
    production_material_summary_fields,
    production_order_fields,
    production_order_line_fields,
    production_request_fields,
    production_rework_fields
)

from ..core.resources import BaseDeleteResource, BaseGetResource, BasePatchResource, BasePostResource

from ..core.utils import success_response, error_response


class ProductionOrderPostResource(BasePostResource):
    service_create = staticmethod(ProductionOrderService.create_obj)
    output_fields = production_order_fields
    
class ProductionOrderGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionOrderService.get_obj)
    schema_list = staticmethod( lambda: ProductionOrderService.get_obj_list(request.args.to_dict()))
    output_fields = production_order_fields

class ProductionOrderDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(ProductionOrderService.delete_obj)
    service_get = staticmethod(ProductionOrderService.get_obj)

class ProductionRequestGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionRequestServices.get_obj)
    schema_list = staticmethod( lambda: ProductionRequestServices.get_obj_list(request.args.to_dict()))
    output_fields = production_request_fields

"""

class ProductionRequestPostResource(BasePostResource):
    service_create = staticmethod(ProductionRequestService.create_obj)
    output_fields = production_request_fields











class ProductionMaterialSummaryGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionMaterialSummaryService.get_obj)
    schema_list = staticmethod( lambda: ProductionMaterialSummaryService.get_obj_list(request.args.to_dict()))
    output_fields = production_material_summary_fields

class ProductionMaterialDetailsGetResource(BaseGetResource):
    schema_get = staticmethod(ProductionMaterialExplosionService.get_obj)
    schema_list = staticmethod( lambda: ProductionMaterialExplosionService.get_obj_list(request.args.to_dict()))
    output_fields = production_material_detail_fields



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