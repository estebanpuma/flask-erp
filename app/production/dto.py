from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from datetime import date
from ..core.dto_base import MyBase
from decimal import Decimal


class OperationDTO(MyBase):
    name: str
    job_id: int
    goal: Optional[str] = None
    kpi: Optional[str] = None
    responsible:  Optional[str] = None

class OperationPatchDTO(MyBase):
    name: Optional[str]=None
    goal: Optional[str] = None
    kpi: Optional[str] = None
    responsible: Optional[str] = None

class OperationStatusDTO(MyBase):
    is_active: bool


class ProductionOrderLineDTO(BaseModel):
    product_variant_id: int
    quantity: int = Field(..., gt=0)
    

class ProductionOrderCreateDTO(BaseModel):
    production_request_ids: List[int] = Field(min_length=1, description='Debe ingresar un requerimiento de produccion')
    start_date: date
    end_date: Optional[date] = None
    workers_available: int = Field(..., gt=0)
    total_overtime_hours: Optional[int] = Field(0, ge=0)

    class Config:
        from_attributes = True

    @model_validator(mode="after")
    def check_dates_and_lines(self):
        if self.end_date < self.start_date:
            raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio.")
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

