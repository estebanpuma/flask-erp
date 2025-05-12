from flask_restful import Resource

from ..core.resources import BaseGetResource, BasePostResource, BasePatchResource, BaseDeleteResource

from .services import SaleServices

from .schemas import sale_order_fields, sale_order_product_fields

from .validations import validate_sale_order_data



class SaleOrderCreateResource(BasePostResource):
    """
    POST /sale_orders
    Crea una orden de venta con productos.
    """
    schema = staticmethod(validate_sale_order_data)
    service_create = staticmethod(SaleServices.create_sale_order)
    output_fields = sale_order_fields


class SaleOrderGetResource(BaseGetResource):
    """
    GET /sale_orders
    Obtener una orden o todas las ordenes de venta con productos.
    """
    schema_get = staticmethod(SaleServices.get_sale)
    schema_list = staticmethod(SaleServices.get_all_sales)
    output_fields = sale_order_fields