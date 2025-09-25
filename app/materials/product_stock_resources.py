from flask import request

from ..core.resources import BaseGetResource
from .product_lot_schemas import product_stock_fields
from .product_stock_services import ProductStockService


class ProductStockGetResource(BaseGetResource):
    schema_list = staticmethod(
        lambda: ProductStockService.get_obj_list(request.args.to_dict())
    )
    output_fields = product_stock_fields
