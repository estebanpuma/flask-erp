from flask import Blueprint

from flask_restful import Api

from .resources import (
    ProductionRequestGetResource,

    ProductionOrderGetResource,
    ProductionOrderPostResource,
    ProductionOrderDeleteResource,

    ProductionOrderLineGetResource,
    ProductionLineGetResource,
    
    ProductionMaterialDetailsGetResource, 
    ProductionMaterialSummaryGetResource, 
   
)

"""

from .resources import (
    ProductionReworkPostResource,
    ProductionReworkGetResource
)
from .resources import (
    ProductionCheckpointPostResource,
    ProductionCheckPointGetResource
)

"""

production_api_bp = Blueprint('production_api', __name__, url_prefix='/api/v1')

production_api = Api(production_api_bp)


production_api.add_resource(ProductionRequestGetResource, '/production-requests', '/production-requests/<int:resource_id>')


production_api.add_resource(ProductionOrderPostResource, '/production-orders')
production_api.add_resource(ProductionOrderGetResource, '/production-orders', '/production-orders/<int:resource_id>')
production_api.add_resource(ProductionOrderDeleteResource, '/production-orders/<int:resource_id>')


production_api.add_resource(ProductionLineGetResource, '/production-lines', '/production-lines/<int:resource_id>')
production_api.add_resource(ProductionOrderLineGetResource, '/production-order/<int:resource_id>/lines' )

production_api.add_resource(ProductionMaterialSummaryGetResource, '/production-order/<int:resource_id>/material-summary' )
production_api.add_resource(ProductionMaterialDetailsGetResource, '/production-line/<int:resource_id>/material-details')

"""

production_api.add_resource(ProductionReworkPostResource, '/production-reworks')
production_api.add_resource(ProductionReworkGetResource, '/production-reworks', '/production-reworks/<int:resource_id>')

production_api.add_resource(ProductionMaterialSummaryGetResource, '/production-material-summary', '/production-material-summary/<int:resource_id>' )
production_api.add_resource(ProductionMaterialDetailsGetResource, '/production-material-details', '/production-material-details/<int:resource_id>')

production_api.add_resource(ProductionCheckPointGetResource, '/production-checkpoints', '/production-checkpoints/<int:resource_id>')
production_api.add_resource(ProductionCheckpointPostResource, '/production-checkpoints')

"""