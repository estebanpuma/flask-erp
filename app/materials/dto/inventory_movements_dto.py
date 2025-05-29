# dto/inventory_movement_dto.py
from pydantic import BaseModel, Field
from typing import Literal, Optional


class InventoryMovementCreateDTO(BaseModel):
    movement_type: Literal['IN', 'OUT']
    lot_id: int
    quantity: float = Field(..., gt=0)
    note: Optional[str] = None

class InventoryAdjustmentDTO(BaseModel):
    lot_id: int
    new_quantity: float = Field(..., ge=0)
    note: Optional[str] = None