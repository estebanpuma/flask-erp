from flask_restful import reqparse, fields

# Define los campos que serán serializados
client_fields = {
    'id': fields.Integer,
    'ruc_or_ci': fields.String,
    'name': fields.String,
    'email': fields.String,
    'client_type': fields.String,
    'city': fields.String,
    'address': fields.String,
    'phone': fields.String
}

canton_fields = {
    'id':fields.Integer,
    'name':fields.String,
    'population':fields.Integer,
    'province_id':fields.Integer,
}

province_fields = {
    'id':fields.Integer,
    'name':fields.String,
    'population':fields.Integer,
    'cantons':fields.Nested(canton_fields)
}

