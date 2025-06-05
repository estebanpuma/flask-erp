from flask import Blueprint

from flask_restful import Api

from . import production_bp

from .resources import (
    ProductionOrderGetResource,
    ProductionOrderPostResource,
    ProductionOrderDeleteResource,
    
    ProductionRequestGetResource,
   
)

"""

from .resources import (
    ProductionRequestPostResource,
    ProductionRequestGetResource
)

from .resources import (
    ProductionReworkPostResource,
    ProductionReworkGetResource
)
from .resources import (
    ProductionCheckpointPostResource,
    ProductionCheckPointGetResource
)
from . resources import (
    ProductionMaterialDetailsGetResource, 
    ProductionMaterialSummaryGetResource, 
    
)
"""

production_api_bp = Blueprint('production_api', __name__, url_prefix='/api/v1')

production_api = Api(production_api_bp)

production_api.add_resource(ProductionOrderPostResource, '/production-orders')
production_api.add_resource(ProductionOrderGetResource, '/production-orders', '/production-orders/<int:resource_id>')
production_api.add_resource(ProductionOrderDeleteResource, '/production-orders/<int:resource_id>')


production_api.add_resource(ProductionRequestGetResource, '/production-requests', '/production-requests/<int:resource_id>')
"""

production_api.add_resource(ProductionRequestPostResource, '/production-requests')
production_api.add_resource(ProductionRequestGetResource, '/production-requests', '/production-requests/<int:resource_id>')




production_api.add_resource(ProductionReworkPostResource, '/production-reworks')
production_api.add_resource(ProductionReworkGetResource, '/production-reworks', '/production-reworks/<int:resource_id>')

production_api.add_resource(ProductionMaterialSummaryGetResource, '/production-material-summary', '/production-material-summary/<int:resource_id>' )
production_api.add_resource(ProductionMaterialDetailsGetResource, '/production-material-details', '/production-material-details/<int:resource_id>')

production_api.add_resource(ProductionCheckPointGetResource, '/production-checkpoints', '/production-checkpoints/<int:resource_id>')
production_api.add_resource(ProductionCheckpointPostResource, '/production-checkpoints')

"""