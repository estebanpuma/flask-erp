from flask import Blueprint
from flask_restful import Api

from .resources import (
    OperationDeleteResource,
    OperationGetResource,
    OperationPatchResource,
    OperationPostResource,
    ProductionLineGetResource,
    ProductionMaterialDetailsGetResource,
    ProductionMaterialSummaryGetResource,
    ProductionOrderDeleteResource,
    ProductionOrderGetResource,
    ProductionOrderLineGetResource,
    ProductionOrderPostResource,
    ProductionRequestGetResource,
    ProductionResourceDeleteResource,
    ProductionResourceGetResource,
    ProductionResourcePatchResource,
    ProductionResourcePostResource,
    VariantUseResourceGetResource,
    VariantUseResourcePatchResource,
    VariantUseResourcePostResource,
)
from .routing_resources import (
    RoutingDeleteResource,
    RoutingGetResource,
    RoutingPostResource,
    RoutingPreviewResource,
)

production_api_bp = Blueprint("production_api", __name__, url_prefix="/api/v1")

production_api = Api(production_api_bp)


production_api.add_resource(RoutingGetResource, "/routings/<int:resource_id>")
production_api.add_resource(RoutingPostResource, "/routings/create")
production_api.add_resource(RoutingPreviewResource, "/routings/preview")
production_api.add_resource(RoutingDeleteResource, "/routings/<int:model_id>")
# production_api.add_resource(RoutingGetResource,       '/routings/<int:resource_id>')

production_api.add_resource(
    ProductionRequestGetResource,
    "/production-requests",
    "/production-requests/<int:resource_id>",
)


production_api.add_resource(ProductionOrderPostResource, "/production-orders")
production_api.add_resource(
    ProductionOrderGetResource,
    "/production-orders",
    "/production-orders/<int:resource_id>",
)
production_api.add_resource(
    ProductionOrderDeleteResource, "/production-orders/<int:resource_id>"
)


production_api.add_resource(
    ProductionLineGetResource,
    "/production-lines",
    "/production-lines/<int:resource_id>",
)
production_api.add_resource(
    ProductionOrderLineGetResource, "/production-order/<int:resource_id>/lines"
)

production_api.add_resource(
    ProductionMaterialSummaryGetResource,
    "/production-order/<int:resource_id>/material-summary",
)
production_api.add_resource(
    ProductionMaterialDetailsGetResource,
    "/production-line/<int:resource_id>/material-details",
)


production_api.add_resource(OperationPostResource, "/operations")
production_api.add_resource(
    OperationGetResource, "/operations", "/operations/<int:resource_id>"
)
production_api.add_resource(OperationDeleteResource, "/operations/<int:resource_id>")
production_api.add_resource(OperationPatchResource, "/operations/<int:resource_id>")


production_api.add_resource(ProductionResourcePostResource, "/production-resources")
production_api.add_resource(
    ProductionResourceGetResource,
    "/production-resources",
    "/production-resources/<int:resource_id>",
)
production_api.add_resource(
    ProductionResourceDeleteResource, "/production-resources/<int:resource_id>"
)
production_api.add_resource(
    ProductionResourcePatchResource, "/production-resources/<int:resource_id>"
)


production_api.add_resource(VariantUseResourcePostResource, "/operations-sheet")
production_api.add_resource(
    VariantUseResourceGetResource,
    "/operations-sheet",
    "/operations-sheet/<int:resource_id>",
)
production_api.add_resource(
    VariantUseResourcePatchResource, "/operations-sheet/<int:resource_id>"
)

"""

production_api.add_resource(ProductionReworkPostResource, '/production-reworks')
production_api.add_resource(ProductionReworkGetResource, '/production-reworks', '/production-reworks/<int:resource_id>')

production_api.add_resource(ProductionMaterialSummaryGetResource, '/production-material-summary', '/production-material-summary/<int:resource_id>' )
production_api.add_resource(ProductionMaterialDetailsGetResource, '/production-material-details', '/production-material-details/<int:resource_id>')

production_api.add_resource(ProductionCheckPointGetResource, '/production-checkpoints', '/production-checkpoints/<int:resource_id>')
production_api.add_resource(ProductionCheckpointPostResource, '/production-checkpoints')

"""
