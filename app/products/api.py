from flask_restful import Api\

from .resources import ProductResource

from . import products_bp


products_api = Api(products_bp)


products_api.add_resource(ProductResource, '/api/v1/products', '/api/v1/products/<int:product_id>')