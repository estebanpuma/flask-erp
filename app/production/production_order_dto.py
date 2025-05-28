# app/dto/production_order_dto.py

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from datetime import date


class ProductionOrderLineInputDTO(BaseModel):
    product_variant_id: int = Field(..., description="ID del producto (variante)")
    quantity: int = Field(..., gt=0, description="Cantidad a producir (debe ser > 0)")
    production_request_id: Optional[int] = Field(None, description="ID del pedido (opcional)")

    @field_validator("product_variant_id", "quantity")
    def positive_ints(cls, v):
        if v <= 0:
            raise ValueError("Debe ser un número positivo.")
        return v


class ProductionOrderCreateDTO(BaseModel):
    start_date: date = Field(..., description="Fecha de inicio de la producción")
    end_date: date = Field(..., description="Fecha de fin de la producción")
    lines: List[ProductionOrderLineInputDTO] = Field(..., description="Líneas de la orden de producción")


    @model_validator(mode="after")
    def check_dates_and_lines(self):
        if self.end_date < self.start_date:
            raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        if not self.lines:
            raise ValueError("La orden debe tener al menos una línea.")
        return self
