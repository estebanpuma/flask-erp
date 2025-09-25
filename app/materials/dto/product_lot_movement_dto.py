# dto/product_lot_movement_dto.py
from typing import Optional

from pydantic import BaseModel, Field


class ProductLotMovementOutDTO(BaseModel):
    product_lot_id: int
    quantity: int = Field(..., gt=0)
    note: Optional[str] = None


class ProductMovementTransferDTO(BaseModel):
    product_lot_id: int
    quantity: int = Field(..., gt=0)
    destination_warehouse_id: int
    note: Optional[str] = None


class ProductLotAdjustmentDTO(BaseModel):
    product_lot_id: int
    new_quantity: float = Field(..., ge=0)
    note: Optional[str] = None
