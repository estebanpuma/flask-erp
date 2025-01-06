from flask_restful import Api
from .resources import StockProductionOrderResource, nextStockOrderCodeResource, ProductionRequestResource, ProductionOrderResource
from .resources import generateProductionOrderCodeResource, ConsolidatedOrdersItemsResource, OrderMaterialsResource
from . import production_bp

production_api = Api(production_bp)


production_api.add_resource(ProductionOrderResource, '/api/v1/production_orders', '/api/v1/production_orders/<int:production_order_id>')

production_api.add_resource(ConsolidatedOrdersItemsResource, '/api/v1/production_orders/<int:order_id>/items')

production_api.add_resource(OrderMaterialsResource, '/api/v1/production_orders/<int:order_id>/materials')

production_api.add_resource(StockProductionOrderResource, '/api/v1/stock_orders', '/api/v1/stock_orders/<int:stock_order_id>')

production_api.add_resource(nextStockOrderCodeResource, '/api/v1/get-next-stock-code')

production_api.add_resource(ProductionRequestResource, '/api/v1/production_requests', '/api/v1/production_requests/<int:production_request_id>')

production_api.add_resource(generateProductionOrderCodeResource, '/api/v1/production_orders/next_code')
