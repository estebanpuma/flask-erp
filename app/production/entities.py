# app/entities/production_entities.py

from math import ceil

from .models import (
    ProductionMaterialDetail,
    ProductionMaterialDetailForRework,
    ProductionMaterialSummary,
    ProductionOrder,
    ProductionOrderLine,
    ProductionRequest,
    ProductionRework,
)


class ProductionRequestEntity:
    def __init__(self, model: ProductionRequest):
        self.model = model

    def update_request(self, status: str):
        """Actualiza el estado de la solicitud"""
        self.model.status = status


class ProductionOrderEntity:
    def __init__(self, model: ProductionOrder):
        self.model = model

    @property
    def total_man_hours(self) -> float:
        """Suma de horas-hombre necesarias de todas las líneas."""

        return sum(
            line_entity.estimated_man_hours() for line_entity in self.line_entities
        )

    @property
    def get_production_duration_days(self) -> int:
        """Duración estimada de la orden, en días."""
        if not self.model.workers_assigned:
            return None
        return ceil(
            self.total_man_hours
            / (self.model.workers_assigned * (self.model.total_overtime_hours + 8))
        )

    @property
    def line_entities(self):
        """Retorna entidades de línea para acceder a su lógica."""
        return [ProductionOrderLineEntity(line) for line in self.model.lines or []]

    @property
    def calculate_material_summary(self):
        """
        Calcula la lista total de materiales por orden de produccion
        devuelve un dict con la lista completa (bom)
        """
        summary = {}
        for line in self.model.lines:
            for material in line.materials:
                mat_id = material.material_id
                qty = material.quantity_needed

                if mat_id in summary:
                    summary[mat_id] += qty
                else:
                    summary[mat_id] = qty
        return summary

    def update_plan(self, workers_assigned: int, overtime_hours: float):
        """Actualiza la planificación global de la orden."""
        self.model.workers_assigned = workers_assigned
        self.model.total_overtime_hours = overtime_hours


class ProductionOrderLineEntity:
    def __init__(self, model: ProductionOrderLine):
        self.model = model

    def estimated_man_hours(self, standar_time: float = None) -> float:
        """Horas hombre totales para esta línea."""
        if standar_time is None:
            standard_hour = (
                self.model.product_variant.standar_time
                if self.model.product_variant
                else 0
            )
            return self.model.quantity * float(standard_hour)
        standard_hour = standar_time
        return self.model.quantity * standard_hour

    @property
    def production_duration_days(self) -> int:
        """Duración estimada de la línea, en días."""
        if not self.model.workers_assigned:
            return None
        return ceil(self.estimated_man_hours / (self.model.workers_assigned * ()))

    def update_plan(self, workers_assigned: int, overtime_hours: float):
        """Actualiza la planificación de esta línea."""
        self.model.workers_assigned = workers_assigned
        self.model.overtime_hours = overtime_hours


class ProductionMaterialDetailEntity:
    def __init__(self, model: ProductionMaterialDetail):
        self.model = model

    @property
    def total_quantity_needed(self) -> float:
        """
        Cantidad total considerando el porcentaje de desperdicio.
        """
        waste_factor = 1 + (self.model.waste_percentage or 0) / 100.0
        return (self.model.quantity_needed or 0) * waste_factor

    def update_reserved(self, quantity_reserved: float):
        """
        Actualiza la cantidad reservada.
        """
        self.model.quantity_reserved = quantity_reserved

    def update_delivered(self, quantity_delivered: float):
        """
        Actualiza la cantidad entregada real.
        """
        self.model.quantity_delivered = quantity_delivered


class ProductionMaterialSummaryEntity:
    def __init__(self, model: ProductionMaterialSummary):
        self.model = model

    @property
    def pending_quantity(self) -> float:
        """
        Calcula la cantidad pendiente de reservar.
        """
        return (self.model.total_quantity_needed or 0) - (
            self.model.quantity_reserved or 0
        )

    def update_reserved(self, quantity_reserved: float):
        self.model.quantity_reserved = quantity_reserved

    def update_pending(self, quantity_pending: float):
        self.model.quantity_pending = quantity_pending


class ProductionReworkEntity:
    def __init__(self, model: ProductionRework):
        self.model = model

    @property
    def additional_man_hours(self) -> float:
        """
        Horas hombre adicionales por reproceso.
        """
        return self.model.additional_hours or 0.0

    @property
    def has_additional_materials(self) -> bool:
        return self.model.additional_materials or False

    @property
    def rework_materials(self):
        """
        Devuelve las entidades de materiales asociados al reproceso.
        """
        return [
            ProductionMaterialDetailForReworkEntity(m)
            for m in self.model.rework_materials or []
        ]


class ProductionMaterialDetailForReworkEntity:
    def __init__(self, model: ProductionMaterialDetailForRework):
        self.model = model

    @property
    def material_used(self) -> float:
        """
        Cantidad usada de material para el reproceso.
        """
        return self.model.quantity_used or 0.0
