# dto/product_lot_movement_dto.py
from pydantic import BaseModel, Field
from typing import Optional, Literal


class ProductLotMovementCreateDTO(BaseModel):
    product_lot_id: int
    movement_type: Literal['IN', 'OUT']
    quantity: float = Field(..., gt=0)
    note: Optional[str] = None
    source_type: Optional[str] = None  # Ej: 'SaleOrder', 'StockOrder'
    source_id: Optional[int] = None

class ProductLotAdjustmentDTO(BaseModel):
    product_lot_id: int
    new_quantity: float = Field(..., ge=0)
    note: Optional[str] = None
