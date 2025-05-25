from flask_restful import Resource, request, marshal_with, marshal_with_field, marshal

from ..core.resources import BaseGetResource, BasePostResource, BasePatchResource, BaseDeleteResource

from .services import SaleOrderService

from .schemas import sale_order_fields, sale_order_line_fields

from ..core.utils import *
from ..core.exceptions import AppError


class SaleOrderPostResource(BasePostResource):
    service_create = staticmethod(SaleOrderService.create_obj)
    output_fields = sale_order_fields

class SaleOrderPatchResource(BasePatchResource):
    service_get = staticmethod(SaleOrderService.get_obj)
    service_patch = staticmethod(SaleOrderService.patch_obj)
    output_fields = sale_order_fields

class SaleOrderGetResource(BaseGetResource):
    schema_get = staticmethod(SaleOrderService.get_obj)
    schema_list = staticmethod(lambda: SaleOrderService.get_obj_list(request.args.to_dict()))
    output_fields = sale_order_fields


class SaleOrderDeleteResource(BaseDeleteResource):
    service_get = staticmethod(SaleOrderService.get_obj)
    service_delete = staticmethod(SaleOrderService.delete_obj)


class SaleOrderCancelResource(Resource):
    def patch(self, resource_id):
        try:
            data = request.get_json()
            reason = data.get("reason", "")
            order = SaleOrderService.cancel_obj(resource_id, reason)
            return success_response(marshal(order, sale_order_fields, "Orden cancelada correctamente."))
        except AppError as e:
            return validation_error_response(str(e))


class SaleOrderLineDeleteResource(Resource):
    def delete(self, order_id, line_id):
        try:
            SaleOrderService.delete_line(order_id, line_id)
            return success_response("Línea eliminada correctamente")
        except AppError as e:
            return validation_error_response(e)
        

class SaleOrderLinePostResource(Resource):
    def post(self, order_id):
        try:
            data = request.get_json()
            line = SaleOrderService.add_line(order_id, data)
            
            return success_response(marshal(line, sale_order_line_fields), 201)
            
        except AppError as e:
            return validation_error_response(str(e))
        
class SaleOrderLinePatchResource(Resource):
    def patch(self, order_id, line_id):
        try:
            data = request.get_json()
            line = SaleOrderService.patch_line(order_id, line_id, data)
            return success_response(marshal(line, sale_order_line_fields,"Línea actualizada correctamente" ))
        except AppError as e:
            return validation_error_response(str(e))
        
        
