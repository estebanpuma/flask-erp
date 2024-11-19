from flask_restful import Api
from .resources import StockProductionOrderResource, nextStockOrderCodeResource
from . import production_bp

production_api = Api(production_bp)



production_api.add_resource(StockProductionOrderResource, '/api/v1/stock_orders', '/api/v1/stock_orders/<int:stock_order_id>')

production_api.add_resource(nextStockOrderCodeResource, '/api/v1/get-next-stock-code')