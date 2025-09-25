# dto/supplier_dto.py
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SupplierCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, strip_whitespace=True)
    ruc_or_ci: str = Field(..., min_length=10, max_length=13, strip_whitespace=True)
    phone: Optional[str] = Field(None, max_length=20, strip_whitespace=True)
    email: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    address: Optional[str] = Field(None, max_length=200, strip_whitespace=True)

    @field_validator("ruc_or_ci")
    def validate_ruc_or_ci_length(cls, v: str) -> str:
        if len(v) not in {10, 13}:
            raise ValueError("ruc_or_ci debe tener exactamente 10 o 13 caracteres")
        return v


class SupplierUpdateDTO(BaseModel):
    phone: Optional[str] = Field(None, max_length=20, strip_whitespace=True)
    email: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    address: Optional[str] = Field(None, max_length=200, strip_whitespace=True)
