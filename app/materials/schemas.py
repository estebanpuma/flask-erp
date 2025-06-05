from flask_restful import fields

material_group_output_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String,
}

material_output_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'detail': fields.String,
    'unit': fields.String,
    'group_id': fields.Integer,
}

material_stock_fields = {
    'id': fields.Integer,
    'material_id': fields.Integer,
    'warehouse_id': fields.Integer,
    'quantity': fields.Float,
    'quantity_available': fields.Float
}
