# app.py o donde registres

from .api import production_api
from .routing_resources import (
    RoutingDeleteResource,
    RoutingGetResource,
    RoutingPostResource,
    RoutingPreviewResource,
)

production_api.add_resource(RoutingGetResource, "/routings/<int:resource_id>")
production_api.add_resource(RoutingPostResource, "/routings/create")
production_api.add_resource(RoutingPreviewResource, "/routings/preview")
production_api.add_resource(RoutingDeleteResource, "/routings/<int:model_id>")
