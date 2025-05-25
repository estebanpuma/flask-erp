from flask import current_app
from ..core.exceptions import ValidationError, NotFoundError
from ..core.origin_factory import OriginFactory
from ..common.parsers import parse_str, parse_int, parse_float, parse_date, parse_bool

from .models import (
    ProductionRequest,
    ProductionOrder,
    ProductionOrderLine,
    ProductionCheckpoint,
    ProductionMaterialDetail,
    ManHourEstimate,
    ProductionRework,
    ProductionMaterialDetailForRework,
)

class ProductionRequestEntity:
    def __init__(self, data: dict):
        self.origin_type = parse_str(data.get("origin_type"), field="origin_type")
        self.origin_id = parse_int(data.get("origin_id"), field="origin_id")
        self.purpose = parse_str(data.get("purpose", ""), field="purpose", nullable=True)
        self.title = parse_str(data.get("title", ""), field="title", nullable=True)
        self.notes = data.get("notes")
        self.status = data.get("status", "Pendiente")
        self.created_by_user_id = parse_int(data.get("created_by_user_id"), field="created_by_user_id")

        self.validate()

    def validate(self):
        existing = ProductionRequest.query.filter_by(origin_type=self.origin_type, origin_id=self.origin_id).first()
        if existing:
            raise ValidationError("Ya existe una solicitud de producción para este origen.")
        # Validar existencia del origen usando Factory
        OriginFactory.get_origin(self.origin_type, self.origin_id)

    def to_model(self):
        return ProductionRequest(
            origin_type=self.origin_type,
            origin_id=self.origin_id,
            purpose=self.purpose,
            title=self.title,
            notes=self.notes,
            status=self.status,
            created_by_user_id=self.created_by_user_id
        )


class ProductionOrderEntity:
    def __init__(self, data: dict):
        self.lines_data = data.get("lines", [])
        if not self.lines_data or not isinstance(self.lines_data, list):
            raise ValidationError("La orden de producción debe contener al menos una línea.")
        self.production_request_id = parse_int(data.get("production_request_id"), field="production_request_id")
        self.start_date = parse_date(data.get("start_date"))  # validar formato si es necesario
        self.end_date = parse_date(data.get("end_date"))

        self.validate()

    def validate(self):
        if not self.production_request_id:
            raise ValidationError("Se requiere production_request_id.")       
    
    def get_lines(self, order_id):
        #if self.production_request.origin_type != "sale_order":
            #raise ValidationError("Por ahora solo se soporta la generación automática desde pedidos de venta.")

        order = OriginFactory.get_origin(self.production_request.origin_type, self.production_request.origin_id)
        lines = []

        for ol in order.lines:
            est = ManHourEstimate.query.filter_by(product_id=ol.product_variant.product_id).first()
            hours = ol.quantity * est.hours_per_unit if est else None

            if not est:
                current_app.logger.warning(f"⚠️ Producto {ol.product_variant.product_id} sin estimación de horas hombre.")

            lines.append(ProductionOrderLine(
                production_order_id=order_id,
                product_variant_id=ol.product_variant_id,
                size_id=ol.size_id,
                quantity=ol.quantity,
                estimated_hours=hours
            ))

        if not lines:
            raise ValidationError("El pedido no contiene líneas para producir.")

        return lines

    def to_model(self):
        return ProductionOrder(
            production_request_id=self.production_request_id,
            start_date=self.start_date,
            end_date=self.end_date,
            status="Pendiente"
        )

    @staticmethod
    def calculate_total_man_hours(order):
        total = sum([line.estimated_hours or 0 for line in order.lines])
        order.total_man_hours = total


class ProductionOrderLineEntity:
    def __init__(self, data: dict):
        self.product_variant_id = parse_int(data.get("product_variant_id"), field="product_variant_id")
        self.size_id = parse_int(data.get("size_id"), field="size_id")
        self.quantity = parse_int(data.get("quantity"), field="quantity", min_value=1)

        self.validate()

    def validate(self):
        if self.quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

    def to_model(self, production_order_id):
        estimate = ManHourEstimate.query.filter_by(product_id=self.product_variant_id).first()
        if not estimate:
            raise ValidationError("No se encontró estimación de horas para el producto.")

        estimated_hours = self.quantity * estimate.hours_per_unit

        return ProductionOrderLine(
            production_order_id=production_order_id,
            product_variant_id=self.product_variant_id,
            size_id=self.size_id,
            quantity=self.quantity,
            estimated_hours=estimated_hours
        )


class ProductionCheckpointEntity:
    STAGE_ORDER = ["corte", "aparado", "armado", "terminado"]

    @staticmethod
    def validate_stage_progression(order_line, new_stage):
        stages = [c.stage for c in order_line.checkpoints if c.completed]
        if ProductionCheckpointEntity.STAGE_ORDER.index(new_stage) > len(stages):
            raise ValidationError(f"No puedes completar la etapa '{new_stage}' antes de completar las anteriores.")


class ProductionMaterialDetailEntity:
    @staticmethod
    def calculate_total_needed(base_quantity, base_material_qty, waste_percentage):
        return round(base_quantity * base_material_qty * (1 + (waste_percentage or 0)/100), 3)


class ProductionReworkEntity:
    def __init__(self, data: dict):
        self.checkpoint_id = parse_int(data.get("checkpoint_id"), field="checkpoint_id")
        self.reason = parse_str(data.get("reason"), field="reason")
        self.additional_hours = parse_float(data.get("additional_hours", 0), field="additional_hours", nullable=True)
        self.additional_materials = bool(data.get("additional_materials", False))

        self.validate()

    def validate(self):
        if not self.checkpoint_id:
            raise ValidationError("Se requiere checkpoint_id para reproceso.")
        if not self.reason:
            raise ValidationError("Debe especificar el motivo del reproceso.")

    def to_model(self):
        return ProductionRework(
            checkpoint_id=self.checkpoint_id,
            reason=self.reason,
            additional_hours=self.additional_hours,
            additional_materials=self.additional_materials
        )


class ProductionMaterialDetailForReworkEntity:
    def __init__(self, data: dict):
        self.rework_id = parse_int(data.get("rework_id"), field="rework_id")
        self.material_id = parse_int(data.get("material_id"), field="material_id")
        self.quantity_used = parse_float(data.get("quantity_used"), field="quantity_used")

        self.validate()

    def validate(self):
        if self.quantity_used <= 0:
            raise ValidationError("La cantidad utilizada debe ser mayor que cero.")

    def to_model(self):
        return ProductionMaterialDetailForRework(
            rework_id=self.rework_id,
            material_id=self.material_id,
            quantity_used=self.quantity_used
        )
