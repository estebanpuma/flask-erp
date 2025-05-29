from flask_restful import Api

from flask import Blueprint

from .resources import (
    MaterialBulkUploadResource,
    MaterialDeleteResource,
    MaterialGetResource,
    MaterialPatchResource,
    MaterialPostResource,

    MaterialGroupDeleteResource,
    MaterialGroupGetResource,
    MaterialGroupPatchResource,
    MaterialGroupPostResource
)

from .material_lot_resources import (
    MaterialLotDeleteResource,
    MaterialLotGetResource,
    MaterialLotPatchResource,
    MaterialLotPostResource,

    InventoryMovementAdjustResource,
    InventoryMovementGetResource,
    InventoryMovementPostResource,
)

from .product_lot_resources import (
    ProductlLotDeleteResource,
    ProductLotAdjustResource,
    ProductLotGetResource,
    ProductLotPatchResource,
    ProductLotPostResource,

    ProductLotMovementGetResource,
    ProductLotMovementPostResource,
)


materials_api_bp = Blueprint('materials_api_bp', __name__, url_prefix='/api/v1')


materials_api = Api(materials_api_bp)
materials_api.add_resource(MaterialGroupPostResource, '/material_groups')
materials_api.add_resource(MaterialGroupGetResource, '/material_groups', '/material_groups/<int:resource_id>')
materials_api.add_resource(MaterialGroupPatchResource, '/material_groups/<int:resource_id>')
materials_api.add_resource(MaterialGroupDeleteResource, '/material_groups/<int:resource_id>')


materials_api.add_resource(MaterialPostResource, '/materials')
materials_api.add_resource(MaterialGetResource, '/materials', '/materials/<int:resource_id>')
materials_api.add_resource(MaterialPatchResource, '/materials/<int:resource_id>')
materials_api.add_resource(MaterialDeleteResource, '/materials/<int:resource_id>')
materials_api.add_resource(MaterialBulkUploadResource, "/materials/upload-excel")


materials_api.add_resource(MaterialLotPostResource, '/material-lots')
materials_api.add_resource(MaterialLotGetResource, '/material-lots', '/material-lots/<int:resource_id>')
materials_api.add_resource(MaterialLotPatchResource, '/material-lots/<int:resource_id>')
materials_api.add_resource(MaterialLotDeleteResource, '/material-lots/<int:resource_id>')


materials_api.add_resource(InventoryMovementPostResource, '/material-movements')
materials_api.add_resource(InventoryMovementGetResource, '/material-movements', '/material-movements/<int:resource_id>')
materials_api.add_resource(InventoryMovementAdjustResource, '/material-adjusts')


materials_api.add_resource(ProductLotPostResource, '/product-lots')
materials_api.add_resource(ProductLotGetResource, '/product-lots', '/product-lots/<int:resource_id>')
materials_api.add_resource(ProductLotPatchResource, '/product-lots/<int:resource_id>')
materials_api.add_resource(ProductlLotDeleteResource, '/product-lots/<int:resource_id>')
materials_api.add_resource(ProductLotAdjustResource, '/product-adjusts')


materials_api.add_resource(ProductLotMovementPostResource, '/product-lot-movements')
materials_api.add_resource(ProductLotMovementGetResource, '/product-lot-movements', '/product-lot-movements/<int:resource_id>')

