from flask_restful import fields

payment_method_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String
}

