# dto/product_lot_dto.py
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ProductLotCreateDTO(BaseModel):
    lot_number: str = Field(..., min_length=1, max_length=50, strip_whitespace=True)
    product_variant_id: int
    warehouse_id: int
    quantity: float = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0)
    production_order_id: int
    received_date: Optional[date] = None


class ProductLotUpdateDTO(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    unit_cost: Optional[float] = Field(None, ge=0)
    warehouse_id: Optional[int] = None
