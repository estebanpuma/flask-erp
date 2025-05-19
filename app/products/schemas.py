from flask_restful import fields, reqparse

from flask_restful import fields


color_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'hex_value': fields.String,
    'name': fields.String,
    'description': fields.String
}

material_fields ={
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'detail': fields.String,
    'unit': fields.String,
    'stock': fields.Float,
    'material_group_id': fields.Integer,
    'current_price': fields.Float
}


# Material del BOM
material_detail_fields = {
    'id': fields.Integer,
    'material_id': fields.Integer,
    'serie_id': fields.Integer,
    'unit': fields.String(attribute='material.unit'),
    'quantity': fields.Float
}

# Variante
variant_fields = {
    'id': fields.Integer,
    'size_id': fields.Integer,
    'size': fields.Integer(attribute='size.value'),
    'code': fields.String,
    'barcode': fields.String,
    'stock': fields.Float,
    'colors': fields.List(fields.Nested(color_fields)),
    'materials': fields.List(fields.Nested(material_detail_fields))
}

variant_material_fields = {
    'id': fields.Integer,
    'variant_id': fields.Integer,
    'material_id': fields.Integer,
    'serie_id': fields.Integer,
    'quantity': fields.Float,
    'unit': fields.String(attribute='material.unit'),
    'material_name': fields.String(attribute='material.name'),
    'material_code': fields.String(attribute='material.code'),
    'serie_name': fields.String(attribute='serie.name'),
}

# Producto principal
product_fields = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'description': fields.String,
    'line_id': fields.Integer,
    'sub_line_id': fields.Integer,
    'variants': fields.List(fields.Nested(variant_fields)),
}

variant_image_fields = {
    'id': fields.Integer,
    'variant_id': fields.Integer,
    'file_name': fields.String,
    'file_path': fields.String
}


# Variante principal
product_variant_fields = {
    'id': fields.Integer,
    'product_id': fields.Integer,
    'size_id': fields.Integer,
    'code': fields.String,
    'barcode': fields.String,
    'stock': fields.Float,
    'colors': fields.List(fields.Nested(color_fields)),
    'materials': fields.List(fields.Nested(variant_material_fields)),
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