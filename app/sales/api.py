from flask_restful import Api

from flask import Blueprint

from .resources import (SaleOrderCancelResource,  SaleOrderLineDeleteResource, 
                        SaleOrderLinePatchResource, SaleOrderLinePostResource, 
                        SaleOrderPatchResource, SaleOrderPostResource,
                        SaleOrderGetResource, SaleOrderDeleteResource)


sales_api_bp = Blueprint('sales_api', __name__, url_prefix='/api/v1')

sales_api = Api(sales_api_bp)

# Sale Order (cabecera)
sales_api.add_resource(SaleOrderPostResource, '/sale_orders')

sales_api.add_resource(SaleOrderGetResource, '/sale_orders', '/sale_orders/<int:resource_id>')
sales_api.add_resource(SaleOrderPatchResource, '/sale_orders/<int:resource_id>')
sales_api.add_resource(SaleOrderDeleteResource, '/sale_orders/<int:resource_id>')
sales_api.add_resource(SaleOrderCancelResource, '/sale_orders/<int:resource_id>/cancel')

# Sale Order Lines (líneas)
sales_api.add_resource(SaleOrderLinePostResource, '/sale_orders/<int:order_id>/lines')
sales_api.add_resource(SaleOrderLinePatchResource, '/sale_orders/<int:order_id>/lines/<int:line_id>')
sales_api.add_resource(SaleOrderLineDeleteResource, '/sale_orders/<int:order_id>/lines/<int:line_id>')