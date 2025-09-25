from flask import Blueprint
from flask_restful import Api

from .material_lot_resources import (
    InventoryMovementAdjustPostResource,
    InventoryMovementGetResource,
    InventoryMovementOutPostResource,
    InventoryMovementTransferPostResource,
    MaterialLotDeleteResource,
    MaterialLotGetByMaterialResource,
    MaterialLotGetResource,
    MaterialLotPatchResource,
    MaterialLotPostResource,
)
from .product_lot_resources import (
    ProductlLotDeleteResource,
    ProductLotAdjustPostResource,
    ProductLotGetResource,
    ProductLotMovementGetResource,
    ProductLotMovementOutPostResource,
    ProductLotMovementTransferPostResource,
    ProductLotPatchResource,
    ProductLotPostResource,
)
from .resources import (
    MaterialBulkUploadResource,
    MaterialDeleteResource,
    MaterialGetResource,
    MaterialGroupDeleteResource,
    MaterialGroupGetResource,
    MaterialGroupPatchResource,
    MaterialGroupPostResource,
    MaterialPatchResource,
    MaterialPostResource,
    MaterialSearchResource,
    MaterialStockGetResource,
    MaterialTotalStockResource,
)

materials_api_bp = Blueprint("materials_api_bp", __name__, url_prefix="/api/v1")


materials_api = Api(materials_api_bp)

materials_api.add_resource(MaterialGroupPostResource, "/material-groups")
materials_api.add_resource(
    MaterialGroupGetResource, "/material-groups", "/material-groups/<int:resource_id>"
)
materials_api.add_resource(
    MaterialGroupPatchResource, "/material-groups/<int:resource_id>"
)
materials_api.add_resource(
    MaterialGroupDeleteResource, "/material-groups/<int:resource_id>"
)


materials_api.add_resource(MaterialPostResource, "/materials")
materials_api.add_resource(
    MaterialGetResource, "/materials", "/materials/<int:resource_id>"
)
materials_api.add_resource(MaterialPatchResource, "/materials/<int:resource_id>")
materials_api.add_resource(MaterialDeleteResource, "/materials/<int:resource_id>")
materials_api.add_resource(MaterialBulkUploadResource, "/materials/upload-excel")

materials_api.add_resource(MaterialSearchResource, "/materials/search")

materials_api.add_resource(MaterialLotPostResource, "/material-lots")
materials_api.add_resource(
    MaterialLotGetResource, "/material-lots", "/material-lots/<int:resource_id>"
)
materials_api.add_resource(MaterialLotPatchResource, "/material-lots/<int:resource_id>")
materials_api.add_resource(
    MaterialLotDeleteResource, "/material-lots/<int:resource_id>"
)

materials_api.add_resource(
    MaterialLotGetByMaterialResource, "/materials/<int:resource_id>/lots"
)


materials_api.add_resource(
    MaterialTotalStockResource, "/material-stocks/<int:material_id>"
)
materials_api.add_resource(MaterialStockGetResource, "/material-stocks")

materials_api.add_resource(InventoryMovementOutPostResource, "/inventory-movements/out")
materials_api.add_resource(
    InventoryMovementGetResource,
    "/inventory-movements",
    "/inventory-movements/<int:resource_id>",
)
materials_api.add_resource(
    InventoryMovementAdjustPostResource, "/inventory-movements/adjust"
)
materials_api.add_resource(
    InventoryMovementTransferPostResource, "/inventory-movements/transfer"
)


materials_api.add_resource(ProductLotPostResource, "/product-lots")
materials_api.add_resource(
    ProductLotGetResource, "/product-lots", "/product-lots/<int:resource_id>"
)
materials_api.add_resource(ProductLotPatchResource, "/product-lots/<int:resource_id>")
materials_api.add_resource(ProductlLotDeleteResource, "/product-lots/<int:resource_id>")


materials_api.add_resource(
    ProductLotMovementOutPostResource, "/product-lot-movements/out"
)
materials_api.add_resource(
    ProductLotAdjustPostResource, "/product-lot-movements/adjust"
)
materials_api.add_resource(
    ProductLotMovementTransferPostResource, "/product-lot-movements/transfer"
)

materials_api.add_resource(
    ProductLotMovementGetResource,
    "/product-lot-movements",
    "/product-lot-movements/<int:resource_id>",
)
