from flask import request, jsonify, current_app

from flask_restful import Resource, marshal_with, abort 

from .services import ProductionServices, StockOrderServices, ProductionRequestServices

from sqlalchemy.exc import SQLAlchemyError

from .schemas import stock_order_simple_fields, stock_order_product_list_fields, stock_order_with_products_fields, production_order_fields
from .schemas import consolidated_items_fields


class StockProductionOrderResource(Resource):

    @marshal_with(stock_order_with_products_fields)
    def get(self, stock_order_id=None):
        try:    
            if stock_order_id:
                spo = StockOrderServices.get_stock_order(stock_order_id)
                return spo, 200 if spo else 404
            
            spos = StockOrderServices.get_all_stock_orders()
            return spos, 200
            
        except SQLAlchemyError as e:
            current_app.logger.warning(f'Error obteninendo StockOrder(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.warning(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")


class ProductionRequestResource(Resource):
    def get(self, production_request_id=None):

        q = request.args.get('ids')
        if q:
            print(q)

        try:
            if production_request_id:
                pr = ProductionRequestServices.get_production_request(production_request_id)
                return pr, 200 if pr else 404
            
            prs = ProductionRequestServices.get_all_production_requests()
            return prs ,200
        
        except SQLAlchemyError as e:
            current_app.logger.warning(f'Error obteniendo ProducionRequest(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.warning(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")
        

class ProductionOrderResource(Resource):

    @marshal_with(production_order_fields)
    def get(self, production_order_id=None):
        
        try:
            if production_order_id:
                po = ProductionServices.get_production_order(production_order_id)
                if po:
                    return po, 200
                abort(404, message="Production order not found")
            po = ProductionServices.get_all_production_orders()
            if po:
                return po, 200
            abort(404, message="Production order not found")

        
        except SQLAlchemyError as e:
            current_app.logger.warning(f'Error obteniendo ProducionOrder(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.warning(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")


class OrderProductionDetail(Resource):

    def get(self, order_id):
        try:
            order_detail = ProductionServices.get_consolidated_items(order_id)
            return order_detail, 200 if order_detail else abort(404, message="Production order detail not found")
        except SQLAlchemyError as e:
            current_app.logger.warning(f'Error obteniendo ProducionOrderDetails(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.warning(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")


class nextStockOrderCodeResource(Resource):

    def get(self):

        try:
            next_code = StockOrderServices.get_next_so_code()
            return next_code, 200 if next_code else abort(500, message=f'Error stockOrder')
        except SQLAlchemyError as e:
            current_app.logger.warning(f'Error next so code(s): {e}')
            abort(500, message=f"Internal server error")
        except Exception as e:
            current_app.logger.warning(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")


class generateProductionOrderCodeResource(Resource):

    def get(self):

        try:
            next_code = ProductionServices.generate_production_order_code()
            return next_code, 200 if next_code else abort(404, message=f'No encontrado')
        except SQLAlchemyError as e:
            current_app.logger.warning(f'Error next so code(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.warning(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")


class ConsolidatedOrdersItemsResource(Resource):

    @marshal_with(consolidated_items_fields)
    def get(self, order_id):
        print('esta es la entrada al recurso a ver si se puede')
        print(f'el id: {order_id}')
        try:
            items = ProductionServices.get_consolidated_items(order_id)
            return items, 200 if items else abort(404, message=f'No encontrado')
            return 'jola'
        except SQLAlchemyError as e:
            current_app.logger.warning(f'Error next so code(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.warning(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")
