from flask_restful import reqparse, fields

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

province_name_fields = {
    'id':fields.Integer,
    'name':fields.String,
    'population':fields.Integer,
}

client_category_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
}
# Define los campos que serán serializados
client_fields = {
    'id': fields.Integer,
    'ruc_or_ci': fields.String,
    'name': fields.String,
    'email': fields.String,
    'client_type': fields.String,
    'city': fields.String,
    'address': fields.String,
    'phone': fields.String,
    'province': fields.Nested(province_name_fields),
    'canton':fields.Nested(canton_fields)
}

contact_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "email": fields.String,
    "phone": fields.String,
    "position": fields.String,
    "notes": fields.String,
    "birth_date": fields.String,
    "client_id": fields.Integer
}

