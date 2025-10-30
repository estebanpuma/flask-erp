# schemas/supplier_fields.py
from flask_restful import fields

supplier_contact_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "position": fields.String,
    "email": fields.String,
    "phone": fields.String,
    "is_primary": fields.Boolean,
}


supplier_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "ruc_or_ci": fields.String,
    "address": fields.String,
    "notes": fields.String,
    "contacts": fields.List(fields.Nested(supplier_contact_fields)),
}
