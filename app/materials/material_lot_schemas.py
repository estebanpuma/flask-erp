# schemas/material_lot_fields.py
from flask_restful import fields

material_lot_fields = {
    'id': fields.Integer,
    'lot_number': fields.String,
    'material_id': fields.Integer,
    'warehouse_id': fields.Integer,
    'quantity': fields.Float,
    'unit_cost': fields.Float,
    'supplier_id': fields.Integer,
    'received_date': fields.DateTime(dt_format='iso8601'),
}



inventory_movement_fields = {
    'id': fields.Integer,
    'lot_id': fields.Integer,
    'movement_type': fields.String,
    'item_type': fields.String,
    'movement_trigger': fields.String,
    'document_number': fields.String,
    'warehouse_id': fields.Integer,
    'responsible_id': fields.Integer,
    'date': fields.DateTime(dt_format='iso8601'),
    'quantity': fields.Float,
    'note': fields.String,
}

