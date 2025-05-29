# dto/supplier_dto.py
from pydantic import BaseModel, Field
from typing import Optional


class SupplierCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, strip_whitespace=True)
    ruc_or_ci: str = Field(..., min_length=1, max_length=20, strip_whitespace=True)
    phone: Optional[str] = Field(None, max_length=20, strip_whitespace=True)
    email: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    address: Optional[str] = Field(None, max_length=200, strip_whitespace=True)


class SupplierUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, strip_whitespace=True)
    ruc_or_ci: Optional[str] = Field(None, min_length=1, max_length=20, strip_whitespace=True)
    phone: Optional[str] = Field(None, max_length=20, strip_whitespace=True)
    email: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    address: Optional[str] = Field(None, max_length=200, strip_whitespace=True)
