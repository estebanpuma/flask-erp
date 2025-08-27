from flask_restful import fields
from datetime import datetime

# Definimos un campo personalizado para la fecha
class DateFormat(fields.Raw):
    def format(self, value):
        if value is None:
            return None
        return value.strftime('%Y-%m-%d')  # Formato: Año-Mes-Día



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
    'description': fields.String,
  
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
    'category': fields.String,
    'is_active': fields.Boolean
}

size_fields = {
    'id': fields.Integer,
    'value': fields.String,
    'series_id': fields.Integer,
}



meterial_variant_fields = {
    'code': fields.String,
    'name': fields.String,
    'unit': fields.String,
}

product_variant_material_detail_fields = {
    'id': fields.Integer,
    'material_id': fields.Integer,
    'variant_id': fields.Integer,
    'quantity': fields.Float,
    'material': fields.Nested(meterial_variant_fields)
}

product_variant_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'barcode': fields.String,
    'stock': fields.Float,
    'size_id': fields.Integer,
    'design_id': fields.Integer,
    'materials': fields.List(fields.Nested(product_variant_material_detail_fields)),
    'size': fields.Nested(size_fields)
}

variants_small = {
    'id': fields.Integer,
    'code': fields.String,
    'stock': fields.Float,
    'size': fields.Nested(size_fields)
}

small_product_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String,
    'line_id': fields.Integer,
    'sub_line_id': fields.Integer,
    'target_id': fields.Integer,
    'collection_id': fields.Integer,
    'line': fields.Nested(line_fields),
    'subline': fields.Nested(line_fields),
    'target': fields.Nested(line_fields),
    'collection': fields.Nested(line_fields),
}
color_names_field = fields.List(fields.String(attribute='name'), attribute='colors')

design_images ={
    'id': fields.Integer,
    'filename': fields.String,
    'is_primary': fields.Boolean
}

product_design_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'description': fields.String,
    'product_id': fields.Integer,
    'colors': fields.List(fields.Nested(color_fields)),  # o fields.String si prefieres mostrar nombres
    'color_names':color_names_field,
    'images':fields.List(fields.Nested(design_images)),
    'variants': fields.List(fields.Nested(variants_small)),
    'created_at': DateFormat,
    'is_active': fields.Boolean,
    'product': fields.Nested(small_product_fields),
    'current_price': fields.Float
    
}

product_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String,
    'line_id': fields.Integer,
    'sub_line_id': fields.Integer,
    'target_id': fields.Integer,
    'collection_id': fields.Integer,
    'line': fields.Nested(line_fields),
    'subline': fields.Nested(line_fields),
    'target': fields.Nested(line_fields),
    'collection': fields.Nested(line_fields),
    'designs': fields.List(fields.Nested(product_design_fields)),
    'created_at': fields.String,
    'is_active': fields.Boolean,
    
}

collection_fields ={
    'id': fields.Integer,
    'aux_code': fields.String,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String,
    'line_id': fields.Integer,
    'subline_id': fields.Integer,
    'target_id': fields.Integer,
    'line_code': fields.String(attribute='line.code'),
    'subline_code': fields.String(attribute='sub_line.code'),
    'target_code': fields.String(attribute='target.code'),
    'line_name': fields.String(attribute='line.name'),
    'subline_name': fields.String(attribute='sub_line.name'),
    'target_name': fields.String(attribute='target.name'),
    'n_hormas': fields.Integer,
    
    
}