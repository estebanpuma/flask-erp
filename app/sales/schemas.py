# fields/sales_fields.py
from flask_restful import fields

sale_order_product_fields = {
    'product_id': fields.Integer,
    'qty': fields.Integer,
    'price': fields.String,
    'discount': fields.String,
    'size': fields.Float,
    'notes': fields.String,
}

sale_order_fields = {
    'id': fields.Integer,
    'order_number': fields.String,
    'order_date': fields.String,
    'delivery_date': fields.String,
    'status': fields.String,
    'delivery_address': fields.String,
    'client_id': fields.Integer,
    'sales_person_id': fields.Integer,
    'order_products': fields.List(fields.Nested(sale_order_product_fields)),
}
