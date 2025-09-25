# schemas/material_lot_fields.py
from flask_restful import fields

material_lot_fields = {
    "id": fields.Integer,
    "lot_number": fields.String,
    "material_id": fields.Integer,
    "warehouse_id": fields.Integer,
    "quantity": fields.Float,
    "unit_cost": fields.Float,
    "supplier_id": fields.Integer,
    "received_date": fields.DateTime(dt_format="iso8601"),
    "warehouse": fields.String(attribute="warehouse.name"),
    "lot_unit": fields.String(attribute="material.unit"),
    "material_name": fields.String(attribute="material.name"),
    "material_code": fields.String(attribute="material.code"),
    "supplier_name": fields.String(attribute="supplier.name"),
}


inventory_movement_fields = {
    "id": fields.Integer,
    "lot_id": fields.Integer,
    "movement_type": fields.String,
    "origin_warehouse_id": fields.Integer,
    "destination_warehouse_id": fields.Integer,
    "date": fields.DateTime(dt_format="iso8601"),
    "quantity": fields.Float,
    "note": fields.String,
}
