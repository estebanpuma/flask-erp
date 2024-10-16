from flask import current_app

from flask_restful import Resource, marshal, marshal_with, abort

from sqlalchemy.exc import SQLAlchemyError

from .services import ProductServices
from .schemas import product_fields


class ProductResource(Resource):

    @marshal_with(product_fields)
    def get(self, product_id=None):
        try:
            if product_id:
                product = ProductServices.get_product(product_id)
                return product, 200
            
            products = ProductServices.get_all_products()
            return products, 200
        
        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching users(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message="Unexpected error occurred")
        