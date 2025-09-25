from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PaymentAgreementCreateDTO(BaseModel):
    sale_order_id: int = Field(..., description="ID de la orden de venta asociada")
    amount: float = Field(..., gt=0, description="Monto de la cuota comprometida")
    expected_date: date = Field(..., description="Fecha comprometida de pago")
    notes: Optional[str] = Field(None, max_length=255, description="Notas (opcional)")
    user_id: Optional[int] = Field(None, description="Id del usuario (opcional)")


class PaymentAgreementUpdateDTO(BaseModel):
    amount: Optional[float] = Field(None, gt=0, description="Nuevo monto comprometido")
    expected_date: Optional[date] = Field(None, description="Nueva fecha comprometida")
    notes: Optional[str] = Field(None, max_length=255, description="Notas actualizadas")
    user_id: Optional[int] = Field(None, description="Id del usuario (opcional)")


class PaymentTransactionCreateDTO(BaseModel):
    sale_order_id: int = Field(..., description="ID de la orden de venta asociada")
    amount: float = Field(..., gt=0, description="Monto del pago realizado")
    payment_date: date = Field(..., description="Fecha real del pago")
    method_id: int = Field(..., description="Método de pago")
    notes: Optional[str] = Field(None, max_length=255, description="Notas (opcional)")
    user_id: Optional[int] = Field(None, description="Id del usuario (opcional)")

    @field_validator("payment_date")
    def validate_payment_date(cls, v):
        if v and v > date.today():
            raise ValueError("La fecha real de pago no puede ser en el futuro.")
        return v


class PaymentTransactionUpdateDTO(BaseModel):
    amount: Optional[float] = Field(None, gt=0, description="Nuevo monto del pago")
    payment_date: Optional[date] = Field(None, description="Nueva fecha real de pago")
    method_id: Optional[int] = Field(None, description="Método de pago actualizado")
    notes: Optional[str] = Field(None, max_length=255, description="Notas actualizadas")
    user_id: Optional[int] = Field(None, description="Id del usuario (opcional)")

    @field_validator("payment_date")
    def validate_payment_date(cls, v):
        if v and v > date.today():
            raise ValueError("La fecha real de pago no puede ser en el futuro.")
        return v
