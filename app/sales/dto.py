# sales/dto.py
from datetime import date as _d
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import Field, field_validator

from ..core.dto_base import MyBase  # ← tu clase con validate_with_message
from ..core.enums import OrderStatus


class PaymentAgreementCreateDTO(MyBase):
    amount: Decimal
    expected_date: _d
    notes: Optional[str]


class PaymentTransactionInlineDTO(MyBase):
    amount: Decimal = Field(..., gt=Decimal("0.00"), description="Monto pagado")
    date: Optional[_d] = None
    method_id: int

    @field_validator("date")
    def default_to_today(cls, v):
        """Si no envían 'date', guardamos la fecha de hoy."""

        return v or _d.today()


class SaleOrderLineDTO(MyBase):
    variant_id: int
    quantity: int


class SaleOrderCreateDTO(MyBase):
    order_number: str
    order_date: _d
    due_date: _d
    shipping_address: str
    shipping_province_id: int
    shipping_canton_id: int
    shipping_reference: Optional[str]
    client_id: int
    sales_person_id: int
    discount_rate: Optional[Decimal] = Decimal(0.00)
    notes: Optional[str]
    payment: PaymentTransactionInlineDTO
    lines: List[SaleOrderLineDTO]


class SaleOrderPatchLineDTO(MyBase):
    id: Optional[int] = None  # Si existe, actualiza línea; si no, crea nueva línea
    variant_id: int
    quantity: int
    discount: Optional[float] = 0.0


class SaleOrderPatchDTO(MyBase):
    delivery_date: Optional[str] = None
    delivery_address: Optional[str] = None
    status: Optional[OrderStatus] = None
    discount: Optional[float] = None
    notes: Optional[str] = None
    lines: Optional[List[SaleOrderPatchLineDTO]] = None


class UpdateSaleOrderStatusDTO(MyBase):
    status: Literal["Aprobada", "Pendiente", "Cancelada", "Rechazada"]


class SaleOrderPreviewLineDTO(MyBase):
    variant_id: int
    quantity: int
    discount_rate: Optional[Decimal] = Decimal("0.0")


class SaleOrderPreviewDTO(MyBase):
    discount_rate: Optional[Decimal] = Decimal("0.0")
    lines: List[SaleOrderPreviewLineDTO]
