# dto/material_lot_dto.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class MaterialLotCreateDTO(BaseModel):
    lot_number: str = Field(..., min_length=1, max_length=50, strip_whitespace=True)
    material_id: int
    supplier_id: int
    warehouse_id: int
    quantity: float = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0)
    received_date: Optional[date] = None


class MaterialLotUpdateDTO(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    unit_cost: Optional[float] = Field(None, ge=0)
    warehouse_id: Optional[int] = None
