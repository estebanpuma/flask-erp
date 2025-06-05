# dto/inventory_movement_dto.py
from pydantic import BaseModel, Field
from typing import Literal, Optional
from ...core.enums import InventoryMovementType


class InventoryMovementOutDTO(BaseModel):
    #movement_type: Literal['OUT']
    lot_id: int
    quantity: float = Field(..., gt=0)
    note: Optional[str] = None


class InventoryMovementTransferDTO(BaseModel):
    #movement_type: Literal['TRANSFER']
    lot_id: int
    destination_warehouse_id: int
    note: Optional[str] = None


class InventoryMovementAdjustDTO(BaseModel):
    #movement_type: Literal['ADJUST']
    lot_id: int
    quantity: float = Field(..., gt=0)
    note: Optional[str] = None
