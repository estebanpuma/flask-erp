from flask import request
from flask_restful import Resource, marshal, marshal_with


from .schemas import material_fields

class MaterialResource(Resource):
    
    @marshal_with(material_fields)
    def get(self, material_id=None):

        pass
        
