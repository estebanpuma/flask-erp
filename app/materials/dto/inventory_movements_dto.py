# dto/inventory_movement_dto.py
from typing import Optional

from pydantic import BaseModel, Field


class InventoryMovementOutDTO(BaseModel):
    # movement_type: Literal['OUT']
    lot_id: int
    quantity: float = Field(..., gt=0)
    note: Optional[str] = None


class InventoryMovementTransferDTO(BaseModel):
    # movement_type: Literal['TRANSFER']
    lot_id: int
    destination_warehouse_id: int
    note: Optional[str] = None


class InventoryMovementAdjustDTO(BaseModel):
    # movement_type: Literal['ADJUST']
    lot_id: int
    quantity: float = Field(..., gt=0)
    note: Optional[str] = None
