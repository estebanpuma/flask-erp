from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from datetime import date

class ProductionOrderLineDTO(BaseModel):
    product_variant_id: int
    quantity: int = Field(..., gt=0)
    

class ProductionOrderCreateDTO(BaseModel):
    production_request_ids: List[int]
    start_date: date
    end_date: Optional[date] = None
    workers_available: int = Field(..., gt=0)
    lines: List[ProductionOrderLineDTO]

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def check_dates_and_lines(self):
        if self.end_date < self.start_date:
            raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        if not self.lines:
            raise ValueError("La orden debe tener al menos una línea.")
        return self


class ProductionOrderUpdatePlanDTO(BaseModel):
    workers_assigned: Optional[int] = Field(None, gt=0, description="Número de trabajadores asignados (opcional, debe ser > 0 si está presente)")
    hours_per_shift: Optional[float] = Field(8, gt=0, lt=24, description="las horas por turno no pueden ser menores de 0 o mayores de 24")
    overtime_hours: Optional[float] = Field(0, ge=0, description='Horas extra no pueden ser menores que 0')

    class Config:
        from_attributes = True


class ProductionOrderCompleteDTO(BaseModel):
    product_variant_id: int
    quantity: int = Field(..., gt=0, description='La cantidad debe ser mayor a cero')
    notes: Optional[str] = None

    class Config:
        from_attributes = True

