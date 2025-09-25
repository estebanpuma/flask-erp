from flask import Blueprint
from flask_restful import Api

from .resources import (
    WarehouseDeleteResource,
    WarehouseGetResource,
    WarehousePatchResource,
    WarehousePostResource,
)

inventory_api_bp = Blueprint("inventory", __name__, url_prefix="/api/v1")

inventory_api = Api(inventory_api_bp)

inventory_api.add_resource(
    WarehouseGetResource, "/warehouses", "/warehouses/<int:resource_id>"
)
inventory_api.add_resource(WarehousePostResource, "/warehouses")
inventory_api.add_resource(WarehousePatchResource, "/warehouses/<int:resource_id>")
inventory_api.add_resource(WarehouseDeleteResource, "/warehouses/<int:resource_id>")
