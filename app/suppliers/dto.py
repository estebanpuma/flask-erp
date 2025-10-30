# dto/supplier_dto.py
from typing import Optional

from pydantic import EmailStr, Field, field_validator

from ..core.dto_base import MyBase


class SupplierCreateDTO(MyBase):
    name: str = Field(..., min_length=1, max_length=200, strip_whitespace=True)
    ruc_or_ci: str = Field(..., min_length=10, max_length=13, strip_whitespace=True)
    phone: Optional[str] = Field(None, max_length=20, strip_whitespace=True)
    email: Optional[EmailStr] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=200, strip_whitespace=True)

    @field_validator("ruc_or_ci")
    def validate_ruc_or_ci_length(cls, v: str) -> str:
        if len(v) not in {10, 13}:
            raise ValueError("ruc_or_ci debe tener exactamente 10 o 13 caracteres")
        return v


class SupplierUpdateDTO(MyBase):
    name: Optional[str] = Field(None, max_length=20, strip_whitespace=True)
    address: Optional[str] = Field(None, max_length=200, strip_whitespace=True)
    ruc_or_ci: Optional[str] = Field(None, max_length=13, strip_whitespace=True)
    lifecycle_status: Optional[str] = None


class SupplierContactCreateDTO(MyBase):
    supplier_id: int
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    email: EmailStr | None = None
    position: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    phone: Optional[str] = Field(None, max_length=20, strip_whitespace=True)
    is_primary: Optional[bool] = False

    @field_validator("email", mode="before")
    def validate_email_format(cls, v):
        print("validate_email_format", v)
        if v == "":
            return None
        return v.lower()


class SupplierContactUpdateDTO(MyBase):
    name: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    phone: Optional[str] = Field(None, max_length=20, strip_whitespace=True)
    email: Optional[EmailStr] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    is_primary: Optional[bool] = None
