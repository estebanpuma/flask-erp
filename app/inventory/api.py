from flask import Blueprint
from flask_restful import Api
from .resources import (
    WarehouseGetResource,
    WarehousePatchResource,
    WarehousePostResource
)

inventory_api_bp = Blueprint('inventory', __name__, url_prefix='/api/v1')

inventory_api = Api(inventory_api_bp)

inventory_api.add_resource(WarehouseGetResource, '/inventory/warehouses', '/inventory/warehouses/<int:resource_id>')
inventory_api.add_resource(WarehousePostResource, '/inventory/warehouses')
inventory_api.add_resource(WarehousePatchResource, '/inventory/warehouses/<int:resource_id>')