from flask import Blueprint
from flask_restful import Api

from .resources import (
    SupplierContactGetListResource,
    SupplierContactGetResource,
    SupplierContactPatchResource,
    SupplierContactPostResource,
    SupplierGetResource,
    SupplierPatchResource,
    SupplierPostResource,
)

suppliers_api_bp = Blueprint("suppliers", __name__, url_prefix="/api/v1")

suppliers_api = Api(suppliers_api_bp)

suppliers_api.add_resource(
    SupplierGetResource, "/suppliers", "/suppliers/<int:resource_id>"
)
suppliers_api.add_resource(SupplierPostResource, "/suppliers")
suppliers_api.add_resource(SupplierPatchResource, "/suppliers/<int:resource_id>")


# ----------------------------Contact--------------------------------
suppliers_api.add_resource(
    SupplierContactGetResource,
    "/suppliers/contacts",
    "/suppliers/contacts/<int:resource_id>",
)
suppliers_api.add_resource(
    SupplierContactGetListResource, "/suppliers/<int:resource_id>/contacts"
)

suppliers_api.add_resource(SupplierContactPostResource, "/suppliers/contacts")
suppliers_api.add_resource(
    SupplierContactPatchResource, "/suppliers/contacts/<int:resource_id>"
)
