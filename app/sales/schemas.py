# fields/sales_fields.py
from flask_restful import fields


from flask_restful import fields

sale_order_line_fields = {
    "id": fields.Integer,
    "variant_id": fields.Integer,
    "quantity": fields.Integer,
    "price_unit": fields.Float,
    "discount": fields.Float,
    "subtotal": fields.Float,
}

sale_order_fields = {
    "id": fields.Integer,
    "order_number": fields.String,
    "order_date": fields.String,
    "delivery_date": fields.String,
    "status": fields.String,
    "delivery_address": fields.String,
    "client_id": fields.Integer,
    "sales_person_id": fields.Integer,
    "subtotal": fields.Float,
    "discount": fields.Float,
    "tax": fields.Float,
    "total": fields.Float,
    "lines": fields.List(fields.Nested(sale_order_line_fields)),
}
