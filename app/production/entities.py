# app/entities/production_entities.py

from math import ceil
from datetime import date
from .models import (
    ProductionOrder,
    ProductionOrderLine,
    ProductionRequest
)
from ..products.models import ProductVariant


class ProductionRequestEntity:
    def __init__(self, model: ProductionRequest):
        self.model = model
    
    def update_request(self, status:str):
        """Actualiza el estado de la solicitud"""
        self.model.status = status
        

class ProductionOrderEntity:
    def __init__(self, model: ProductionOrder):
        self.model = model

    @property
    def total_man_hours(self) -> float:
        """Suma de horas-hombre necesarias de todas las líneas."""
        return sum(line_entity.man_hours_needed for line_entity in self.line_entities)

    @property
    def total_hours_per_worker(self) -> float:
        """Horas totales que trabaja cada trabajador (normales + extra)."""
        return (self.model.hours_per_shift or 0) + (self.model.overtime_hours or 0)

    @property
    def production_duration_days(self) -> int:
        """Duración estimada de la orden, en días."""
        if not self.model.workers_assigned or not self.total_hours_per_worker:
            return None
        return ceil(self.total_man_hours / (self.model.workers_assigned * self.total_hours_per_worker))

    @property
    def line_entities(self):
        """Retorna entidades de línea para acceder a su lógica."""
        return [ProductionOrderLineEntity(line) for line in self.model.lines or []]

    def update_plan(self, workers_assigned: int, hours_per_shift: float, overtime_hours: float):
        """Actualiza la planificación global de la orden."""
        self.model.workers_assigned = workers_assigned
        self.model.hours_per_shift = hours_per_shift
        self.model.overtime_hours = overtime_hours


class ProductionOrderLineEntity:
    def __init__(self, model: ProductionOrderLine):
        self.model = model

    @property
    def man_hours_needed(self) -> float:
        """Horas hombre totales para esta línea."""
        standard_hour = self.model.product_variant.standard_man_hour or 0
        return self.model.quantity * standard_hour

    @property
    def total_hours_per_worker(self) -> float:
        """Horas totales por trabajador (normales + extras)."""
        return (self.model.hours_per_shift or 0) + (self.model.overtime_hours or 0)

    @property
    def production_duration_days(self) -> int:
        """Duración estimada de la línea, en días."""
        if not self.model.workers_assigned or not self.total_hours_per_worker:
            return None
        return ceil(self.man_hours_needed / (self.model.workers_assigned * self.total_hours_per_worker))

    def update_plan(self, workers_assigned: int, hours_per_shift: float, overtime_hours: float):
        """Actualiza la planificación de esta línea."""
        self.model.workers_assigned = workers_assigned
        self.model.hours_per_shift = hours_per_shift
        self.model.overtime_hours = overtime_hours
