# fields/sales_fields.py
from flask_restful import fields


from flask_restful import fields
from decimal import Decimal


class MyDecimal(fields.Raw):
    def format(self, value):
        if value is None:
            return None
        return format(Decimal(value).quantize(Decimal('0.01')), 'f')

fields.MyDecimal = MyDecimal   # añade al namespace

preview_order_fields = {
    "subtotal": fields.MyDecimal,
    "discount": fields.MyDecimal,
    "total": fields.MyDecimal,
    "taxes": fields.MyDecimal,
}


list_sale_order_line_fields = {
    "id": fields.Integer,
    "variant_id": fields.Integer,
    "quantity": fields.Integer,
    "price_unit": fields.MyDecimal,
    "discount_rate": fields.MyDecimal,
    "subtotal": fields.MyDecimal,
}

size_fields = {
    'id': fields.Integer,
    'value': fields.String,
    'series_id': fields.Integer,
}

variant_fields = {
    "id": fields.Integer,
    "design_id": fields.Integer,
    "code": fields.String,
    "size": fields.Nested(size_fields)
}

sale_order_line_fields = {
    "id": fields.Integer,
    "variant_id": fields.Integer,
    "quantity": fields.Integer,
    "price_unit": fields.MyDecimal,
    "discount_rate": fields.MyDecimal,
    "subtotal": fields.MyDecimal,
    "variant": fields.Nested(variant_fields)
}

client_order_fields = {
    'id': fields.Integer,
    'ruc_or_ci': fields.Integer,
    'name': fields.String,
    'category': fields.String,
    'phone': fields.String
}

sale_order_fields = {
    "id": fields.Integer,
    "order_number": fields.String,
    "order_date": fields.String,
    "due_date": fields.String,
    "payment_status": fields.String,
    "status": fields.String,
    "shipping_address": fields.String,
    "shipping_reference": fields.String,
    "shipping_province_id": fields.Integer,
    "shipping_canton_id": fields.Integer,
    "client_id": fields.Integer,
    "client": fields.Nested(client_order_fields),
    "sales_person_id": fields.Integer,
    "subtotal": fields.MyDecimal,
    "discount_rate": fields.MyDecimal,
    "tax": fields.MyDecimal,
    "tax_rate": fields.MyDecimal,
    "total": fields.MyDecimal,
    "amount_paid": fields.MyDecimal,
    "amount_due":fields.MyDecimal,
    "lines": fields.List(fields.Nested(list_sale_order_line_fields)),
    "notes": fields.String,
}
