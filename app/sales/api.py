from flask_restful import Api

from flask import Blueprint

from .resources import SaleOrderCreateResource


sales_api_bp = Blueprint('sales_api', __name__, url_prefix='/api/v1')

sales_api = Api(sales_api_bp)

sales_api.add_resource(SaleOrderCreateResource, '/sale-orders')
