from flask import request
from flask_restful import Resource, marshal, marshal_with

from .services import MaterialServices
from .schemas import material_fields

class MaterialResource(Resource):
    
    @marshal_with(material_fields)
    def get(self, material_id=None):

        query = request.args.get('q', '').lower()

        if query:
            try:
                results = MaterialServices.search_material(query)
                
                return results, 200 
            
            except Exception as e:
                return str(e), 500


        if material_id:
            material = MaterialServices.get_material(material_id)
            return material, 200
        
        materials = MaterialServices.get_all_materials()
        return materials, 200
        
