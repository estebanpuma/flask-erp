from flask_restful import fields



color_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'hex_value': fields.String,
    'name': fields.String,
    'description': fields.String
}

line_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String
}

subline_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String
}



size_series_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'start_size': fields.Integer,
    'end_size': fields.Integer,
    'is_active': fields.Boolean
}

size_fields = {
    'id': fields.Integer,
    'value': fields.String,
    'series_id': fields.Integer,
}



#neww

product_variant_material_detail_fields = {
    'id': fields.Integer,
    'material_id': fields.Integer,
    'variant_id': fields.Integer,
    'quantity': fields.Float
}

product_variant_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'barcode': fields.String,
    'stock': fields.Float,
    'size_id': fields.Integer,
    'design_id': fields.Integer,
    'materials': fields.List(fields.Nested(product_variant_material_detail_fields))
}

variants_small = {
    'id': fields.Integer,
    'code': fields.String,
    'stock': fields.Float,
}

product_design_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'description': fields.String,
    'product_id': fields.Integer,
    'colors': fields.List(fields.Nested(color_fields)),  # o fields.String si prefieres mostrar nombres
    'variants': fields.List(fields.Nested(variants_small))
}

product_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String,
    'line_id': fields.Integer,
    'sub_line_id': fields.Integer,
    'designs': fields.List(fields.Nested(product_design_fields))
}