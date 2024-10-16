from flask_restful import fields, reqparse

product_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'line_id': fields.String,
    'subline_id': fields.String,
    'desrcription': fields.String
}