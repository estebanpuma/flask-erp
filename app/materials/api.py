from flask_restful import Api

from flask import Blueprint

from .resources import MaterialGroupPostResource, MaterialGroupGetResource, MaterialGroupDeleteResource, MaterialGroupPatchResource

from .resources import MaterialPatchResource, MaterialDeleteResource, MaterialGetResource, MaterialPostResource

from .resources import MaterialBulkUploadResource


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