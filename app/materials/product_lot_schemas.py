# schemas/product_lot_fields.py
from flask_restful import fields

product_lot_fields = {
    "id": fields.Integer,
    "lot_number": fields.String,
    "product_variant_id": fields.Integer,
    "warehouse_id": fields.Integer,
    "quantity": fields.Float,
    "unit_cost": fields.Float,
    "production_order_id": fields.Integer,
    "status": fields.String,
    "received_date": fields.DateTime(dt_format="iso8601"),
}

product_lot_movement_fields = {
    "id": fields.Integer,
    "product_lot_id": fields.Integer,
    "movement_type": fields.String,
    "quantity": fields.Float,
    "date": fields.DateTime(dt_format="iso8601"),
    "note": fields.String,
    "source_type": fields.String,
    "source_id": fields.Integer,
}

product_stock_fields = {
    "id": fields.Integer,
    "product_variant_id": fields.Integer,
    "warehouse_id": fields.Integer,
    "quantity": fields.Float,
}
