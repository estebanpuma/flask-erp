from flask import request, jsonify, current_app

from flask_restful import Resource, marshal_with, abort 

from .services import ProductionSevices

from sqlalchemy.exc import SQLAlchemyError

from .schemas import stock_prod_order_fields

class StockProductionOrderResource(Resource):

    @marshal_with(stock_prod_order_fields)
    def get(self, stock_order_id=None):
        try:
           
                
            if stock_order_id:
                spo = ProductionSevices.get_stock_order(stock_order_id)
                return spo, 200 if spo else 404
            
            spos = ProductionSevices.get_all_stock_orders()
            return spos, 200
            
        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching users(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")
        


class nextStockOrderCodeResource(Resource):

    def get(self):

        try:
            next_code = ProductionSevices.get_next_so_code()
            return next_code, 200 if next_code else 500

        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching users(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")