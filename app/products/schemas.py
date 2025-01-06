from flask_restful import fields, reqparse

product_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'line_id': fields.String,
    'subline_id': fields.String,
    'description': fields.String
}

material_fields ={
    'code': fields.String,
    'name': fields.String,
    'description':fields.String
}

product_material_detail_fields = {
    'id': fields.Integer,
    'product_id': fields.Integer,
    'material_id': fields.Integer,
    'serie_id': fields.Integer,
    'unit': fields.String,
    'quantity': fields.Float,
    'material': fields.List(fields.Nested(material_fields)) 
}

line_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String
}

subline_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String
}

color_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'hex': fields.String,
    'name': fields.String,
    'description': fields.String
}

size_series_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'start_size': fields.Integer,
    'end_size': fields.Integer,
    'is_active': fields.Boolean
}

size_fields = {
    'id': fields.Integer,
    'value': fields.String,
    'series_id': fields.Integer,
}