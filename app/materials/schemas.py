from flask_restful import fields

material_subgroup_output_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "group_id": fields.Integer,
    "count_materials": fields.Integer(attribute="count_materials"),
    "group_name": fields.String(attribute="group.name"),
}


material_group_output_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "name": fields.String,
    "description": fields.String,
    "subgroups": fields.List(fields.Nested(material_subgroup_output_fields)),
    "count_materials": fields.Integer(attribute="count_materials"),
}


material_output_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "name": fields.String,
    "detail": fields.String,
    "unit": fields.String,
    "group_id": fields.Integer,
    "stock": fields.Float(attribute="get_material_total_stock"),
}

material_stock_fields = {
    "id": fields.Integer,
    "material_id": fields.Integer,
    "warehouse_id": fields.Integer,
    "quantity": fields.Float,
    "quantity_available": fields.Float,
}

material_search_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "name": fields.String,
    "detail": fields.String,
    "unit": fields.String,
}
