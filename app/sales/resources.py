from flask_restful import Resource

from ..core.resources import BaseGetResource, BasePostResource, BasePatchResource, BaseDeleteResource

from .services import SaleServices

from .schemas import sale_order_fields, sale_order_product_fields

from .validations import validate_sale_order_data



class SaleOrderCreateResource(BasePostResource):
    """
    Crea una nueva orden de venta.
    """
    schema = staticmethod(validate_sale_order_data)
    service_create = staticmethod(SaleServices.create_order)
    output_fields = sale_order_fields

