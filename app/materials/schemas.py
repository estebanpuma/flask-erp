from flask_restful import fields

material_group_output_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String,
}

material_output_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'detail': fields.String,
    'unit': fields.String,
    'group_id': fields.Integer,
}