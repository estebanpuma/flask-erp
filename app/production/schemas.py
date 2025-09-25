from flask_restful import fields

production_resources_fields = {
    "id": fields.Integer,
    "kind": fields.String,
    "name": fields.String,
    "code": fields.String,
    "qty": fields.Integer,
    "description": fields.String,
    "operation_id": fields.Integer,
    "operation_name": fields.String(attribute="operation.name"),
    "capacity_per_unit": fields.MyDecimal,
    "capacity_unit": fields.String,
    "total_capacity": fields.MyDecimal,
    "is_active": fields.Boolean,
}

variant_resource_usage = {
    "id": fields.Integer,
    "resource_id": fields.Integer,
    "operation_id": fields.Integer,
    "variant_id": fields.Integer,
    "std_min_unit": fields.MyDecimal,
    "operation_name": fields.String(attribute="operation.name"),
    "resource_name": fields.String(attribute="resource.name"),
    "variant_code": fields.String(attribute="variant.code"),
}

op_fields = {
    "id": fields.Integer,
    "code": fields.String,
    "name": fields.String,
    "rate_hour": fields.MyDecimal,
    "mission": fields.String,
    "kpi": fields.String,
    "responsible": fields.String,
    "resources": fields.List(fields.Nested(production_resources_fields)),
    "variant_operations": fields.List(fields.Nested(variant_resource_usage)),
    "is_active": fields.Boolean,
}


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
    "estimated_man_hours": fields.Float,
    "workers_assigned": fields.Integer,
    "overtime_hours": fields.Float,
}

production_order_fields = {
    "id": fields.Integer,
    "status": fields.String,
    "start_date": fields.DateTime(dt_format="iso8601"),
    "end_date": fields.DateTime(dt_format="iso8601"),
    "workers_assigned": fields.Integer,
    "total_overtime_hours": fields.Float,
    "estimated_man_hours": fields.Float,
    "created_at": fields.DateTime(dt_format="iso8601"),
    "lines": fields.List(fields.Nested(production_order_line_fields)),
    "get_production_duration_days": fields.Integer,
    "production_requests": fields.List(fields.Nested(production_request_fields)),
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
