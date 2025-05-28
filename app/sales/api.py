from flask_restful import Api

from flask import Blueprint

from .resources import (
                        SaleOrderPostResource,
                        SaleOrderPatchResource,
                        SaleOrderDeleteResource,
                        SaleOrderGetResource, 
                        SaleOrderPreviewResource
)


sales_api_bp = Blueprint('sales_api', __name__, url_prefix='/api/v1')

sales_api = Api(sales_api_bp)

# Sale Order (cabecera)
sales_api.add_resource(SaleOrderPostResource, '/sale-orders')
sales_api.add_resource(SaleOrderGetResource, '/sale-orders', '/sale-orders/<int:resource_id>')

sales_api.add_resource(SaleOrderPatchResource, '/sale-orders/<int:resource_id>')
sales_api.add_resource(SaleOrderDeleteResource, '/sale-orders/<int:resource_id>')

sales_api.add_resource(SaleOrderPreviewResource, '/sale-orders/preview')

"""


sales_api.add_resource(SaleOrderCancelResource, '/sale_orders/<int:resource_id>/cancel')

# Sale Order Lines (líneas)
sales_api.add_resource(SaleOrderLinePostResource, '/sale_orders/<int:order_id>/lines')
sales_api.add_resource(SaleOrderLinePatchResource, '/sale_orders/<int:order_id>/lines/<int:line_id>')
sales_api.add_resource(SaleOrderLineDeleteResource, '/sale_orders/<int:order_id>/lines/<int:line_id>')
"""