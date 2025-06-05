# sales/dto.py

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date


from ..core.enums import OrderStatus


class PaymentAgreementCreateDTO(BaseModel):
    amount: float
    expected_date: date
    notes: Optional[str]

class SaleOrderLineDTO(BaseModel):
    variant_id: int
    quantity: int
    discount: Optional[float] = 0.0

class SaleOrderCreateDTO(BaseModel):
    order_number: str
    order_date: date
    delivery_date: date
    delivery_address: Optional[str]
    client_id: int
    sales_person_id: int
    discount: Optional[float] = 0.0
    tax: Optional[float] = 0.0
    notes: Optional[str]
    lines: List[SaleOrderLineDTO]
    agreements: List[PaymentAgreementCreateDTO] = Field(..., description="Lista de cuotas/acuerdos de pago")

# sales/dto.py


class SaleOrderPatchLineDTO(BaseModel):
    id: Optional[int] = None # Si existe, actualiza línea; si no, crea nueva línea
    variant_id: int
    quantity: int
    discount: Optional[float] = 0.0

class SaleOrderPatchDTO(BaseModel):
    delivery_date: Optional[str]  = None
    delivery_address: Optional[str] = None

    status: Optional[OrderStatus] = None
    discount: Optional[float] = None
    tax: Optional[float] = None
    notes: Optional[str] = None
    lines: Optional[List[SaleOrderPatchLineDTO]] = None

    










class SaleOrderPreviewLineDTO(BaseModel):
    variant_id: int
    quantity: int
    discount: Optional[float] = 0.0

class SaleOrderPreviewDTO(BaseModel):
    discount: Optional[float] = 0.0
    tax: Optional[float] = 0.0
    lines: List[SaleOrderPreviewLineDTO]
