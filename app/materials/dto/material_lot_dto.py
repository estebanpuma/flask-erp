# dto/material_lot_dto.py
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class MaterialLotCreateDTO(BaseModel):
    lot_number: str = Field(..., min_length=1, max_length=50, strip_whitespace=True)
    material_id: int
    supplier_id: int
    warehouse_id: int
    quantity: float = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0)
    received_date: Optional[date] = None
    note: Optional[str] = None


class MaterialLotUpdateDTO(BaseModel):
    unit_cost: Optional[float] = Field(None, ge=0)
    received_date: Optional[date] = None
    lot_number: str = Field(..., min_length=1, max_length=50, strip_whitespace=True)
    note: Optional[date] = None
