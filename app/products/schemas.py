from flask_restful import fields


# Definimos un campo personalizado para la fecha
class DateFormat(fields.Raw):
    def format(self, value):
        if value is None:
            return None
        return value.strftime("%Y-%m-%d")  # Formato: Año-Mes-Día


color_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "hex_value": fields.String,
    "name": fields.String,
    "description": fields.String,
    "count_products": fields.Integer,
    "is_active": fields.Boolean,
}

line_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "name": fields.String,
    "description": fields.String,
    "count_products": fields.Integer,
    "is_active": fields.Boolean,
    "lifecycle_status": fields.String,
}

subline_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "name": fields.String,
    "description": fields.String,
    "count_products": fields.Integer,
    "is_active": fields.Boolean,
    "lifecycle_status": fields.String,
}


size_series_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "code": fields.String,
    "description": fields.String,
    "start_size": fields.Integer,
    "end_size": fields.Integer,
    "category": fields.String,
    "is_active": fields.Boolean,
    "count_sizes": fields.Integer,
    "lifecycle_status": fields.String,
}


size_fields = {
    "id": fields.Integer,
    "value": fields.String,
    "series_id": fields.Integer,
}


meterial_variant_fields = {
    "code": fields.String,
    "name": fields.String,
    "unit": fields.String,
}

product_variant_material_detail_fields = {
    "id": fields.Integer,
    "material_id": fields.Integer,
    "variant_id": fields.Integer,
    "quantity": fields.Float,
    "material": fields.Nested(meterial_variant_fields),
}

product_variant_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "barcode": fields.String,
    "stock": fields.Float,
    "size_id": fields.Integer,
    "design_id": fields.Integer,
    "materials": fields.List(fields.Nested(product_variant_material_detail_fields)),
    "size": fields.Nested(size_fields),
    "lifecycle_status": fields.String,
    "product_id": fields.Integer,
}

variants_small = {
    "id": fields.Integer,
    "code": fields.String,
    "stock": fields.Float,
    "size": fields.Nested(size_fields),
    "lifecycle_status": fields.String,
    "product_id": fields.Integer,
}

small_product_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "name": fields.String,
    "description": fields.String,
    "line_id": fields.Integer,
    "sub_line_id": fields.Integer,
    "target_id": fields.Integer,
    "collection_id": fields.Integer,
    "line": fields.Nested(line_fields),
    "subline": fields.Nested(line_fields),
    "target": fields.Nested(line_fields),
    "collection": fields.Nested(line_fields),
    "line_name": fields.String(attribute="line.name"),
    "subline_name": fields.String(attribute="sub_line.name"),
    "collection_name": fields.String(attribute="collection.name"),
    "target_name": fields.String(attribute="target.name"),
    "created_at": fields.String,
    "lifecycle_status": fields.String,
}
color_names_field = fields.List(fields.String(attribute="name"), attribute="colors")

# Nuevo esquema para el objeto de asociación ProductDesignImage
design_image_association_fields = {
    "id": fields.Integer(attribute="media_file.id"),
    "filename": fields.String(attribute="media_file.filename"),
    "url": fields.String(attribute="media_file.url"),
    "is_primary": fields.Boolean,
    "order": fields.Integer,
}

product_design_images_fields = {
    "id": fields.Integer,
    "design_id": fields.Integer,
    "media_file_id": fields.Integer,
    "is_primary": fields.Boolean,
    "order": fields.Integer,
    "media_file": fields.Nested(design_image_association_fields),
}

product_design_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "name": fields.String,
    "description": fields.String,
    "product_id": fields.Integer,
    "colors": fields.List(fields.Nested(color_fields)),
    "color_names": color_names_field,
    "images": fields.List(
        fields.Nested(design_image_association_fields), attribute="image_associations"
    ),
    "variants": fields.List(fields.Nested(variants_small)),
    "created_at": DateFormat,
    "is_active": fields.Boolean,
    "product": fields.Nested(small_product_fields),
    "current_price": fields.Float,
    "lifecycle_status": fields.String,
    "old_code": fields.String,
}

product_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "name": fields.String,
    "description": fields.String,
    "line_id": fields.Integer,
    "sub_line_id": fields.Integer,
    "target_id": fields.Integer,
    "collection_id": fields.Integer,
    "line": fields.Nested(line_fields),
    "subline": fields.Nested(line_fields),
    "line_name": fields.String(attribute="line.name"),
    "subline_name": fields.String(attribute="sub_line.name"),
    "collection_name": fields.String(attribute="collection.name"),
    "target_name": fields.String(attribute="target.name"),
    "target": fields.Nested(line_fields),
    "collection": fields.Nested(line_fields),
    "designs": fields.List(fields.Nested(product_design_fields)),
    "created_at": fields.String,
    "is_active": fields.Boolean,
    "old_code": fields.String,
    "lifecycle_status": fields.String,
}

collection_fields = {
    "id": fields.Integer,
    "aux_code": fields.String,
    "code": fields.String,
    "name": fields.String,
    "description": fields.String,
    "line_id": fields.Integer,
    "subline_id": fields.Integer,
    "target_id": fields.Integer,
    "line_code": fields.String(attribute="line.code"),
    "subline_code": fields.String(attribute="sub_line.code"),
    "target_code": fields.String(attribute="target.code"),
    "line_name": fields.String(attribute="line.name"),
    "subline_name": fields.String(attribute="sub_line.name"),
    "target_name": fields.String(attribute="target.name"),
    "is_active": fields.Boolean,
    "last_type_id": fields.Integer,
    "last_type_name": fields.String(attribute="last_type.name"),
    "last_code": fields.String(attribute="last_type.code"),
    "count_products": fields.Integer(attribute="count_products"),
    "lifecycle_status": fields.String,
}


last_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "qty": fields.Integer,
    "size": fields.Integer,
    "status": fields.String,
    "family_id": fields.Integer,
}

last_type_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "code": fields.String,
    "collection_id": fields.Integer,
    "collection_name": fields.String(attribute="collection.name"),
    "lasts": fields.List(fields.Nested(last_fields)),
    "lifecycle_status": fields.String,
}
