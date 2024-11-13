from flask_restful import Api\

from .resources import ProductResource, LineResource, SubLineResource, ColorResource, NextCodeModelResource, SizeSeriesResource
from .resources import ProcessBoomFileResource

from . import products_bp


products_api = Api(products_bp)


products_api.add_resource(ProductResource, '/api/v1/products', '/api/v1/products/<int:product_id>')

products_api.add_resource(LineResource, '/api/v1/lines', '/api/v1/lines/<int:line_id>')

products_api.add_resource(SubLineResource, '/api/v1/sublines', '/api/v1/sublines/<int:subline_id>')

products_api.add_resource(ColorResource, '/api/v1/colors', '/api/v1/colors/<int:color_id>')

products_api.add_resource(SizeSeriesResource, '/api/v1/sizeSeries', '/api/v1/sizeSeries/<int:serie_id>')

products_api.add_resource(ProcessBoomFileResource, '/api/v1/bomfile/upload')

products_api.add_resource(NextCodeModelResource, '/api/v1/next_code_model/<string:line_code>' , '/api/v1/next_code_model/<string:line_code>/<string:subline_code>')
