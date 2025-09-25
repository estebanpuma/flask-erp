from flask_restful import fields

warehouse_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "name": fields.String,
    "description": fields.String,
    "location": fields.String,
}
