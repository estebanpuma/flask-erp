
from flask_restful import Api
from .resources import MaterialResource
from . import inventory_bp

inventory_api = Api(inventory_bp)



inventory_api.add_resource(MaterialResource, '/api/v1/materials', '/api/v1/materials/<int:material_id>')
