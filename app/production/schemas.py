from flask_restful import fields, reqparse

production_request_fields = {
    "id": fields.Integer,
    "origin_type": fields.String,
    "origin_id": fields.Integer,
    "purpose": fields.String,
    "title": fields.String,
    "notes": fields.String,
    "status": fields.String,
    "created_by_user_id": fields.Integer,
    "created_at": fields.DateTime,
}

production_order_line_fields = {
    "id": fields.Integer,
    "production_order_id": fields.Integer,
    "product_variant_id": fields.Integer,
    "size_id": fields.Integer,
    "quantity": fields.Integer,
    "estimated_hours": fields.Float,
}

production_order_fields = {
    "id": fields.Integer,
    "production_request_id": fields.Integer,
    "status": fields.String,
    "start_date": fields.DateTime(dt_format='iso8601'),
    "end_date": fields.DateTime(dt_format='iso8601'),
    "total_man_hours": fields.Float,
    "created_at": fields.DateTime(dt_format='iso8601'),
    "lines": fields.List(fields.Nested(production_order_line_fields))
}

production_material_detail_fields = {
    "id": fields.Integer,
    "order_line_id": fields.Integer,
    "material_id": fields.Integer,
    "quantity_needed": fields.Float,
    "waste_percentage": fields.Float,
    "quantity_reserved": fields.Float,
    "quantity_delivered": fields.Float,
}

production_material_summary_fields = {
    "id": fields.Integer,
    "production_order_id": fields.Integer,
    "material_id": fields.Integer,
    "total_quantity_needed": fields.Float,
    "quantity_reserved": fields.Float,
    "quantity_pending": fields.Float,
}

production_checkpoint_fields = {
    "id": fields.Integer,
    "order_line_id": fields.Integer,
    "stage": fields.String,
    "completed": fields.Boolean,
    "completed_at": fields.DateTime,
}

production_rework_fields = {
    "id": fields.Integer,
    "checkpoint_id": fields.Integer,
    "reason": fields.String,
    "additional_hours": fields.Float,
    "additional_materials": fields.Boolean,
    "created_at": fields.DateTime,
}

production_material_detail_for_rework_fields = {
    "id": fields.Integer,
    "rework_id": fields.Integer,
    "material_id": fields.Integer,
    "quantity_used": fields.Float,
}