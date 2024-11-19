from flask_restful import fields, reqparse


material_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String,
    'unit': fields.String

}
