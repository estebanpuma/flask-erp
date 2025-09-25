# schemas/supplier_fields.py
from flask_restful import fields

supplier_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "ruc_or_ci": fields.String,
    "phone": fields.String,
    "email": fields.String,
    "address": fields.String,
}
