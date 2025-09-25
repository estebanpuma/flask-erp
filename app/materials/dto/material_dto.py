# dto/material_dto.py
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MaterialCreateDTO(BaseModel):
    code: str = Field(..., min_length=1, max_length=20, strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    detail: Optional[str] = None
    unit: Optional[str] = None
    group_id: Optional[int] = None

    @field_validator("code")
    def code_must_be_uppercase(cls, v: str) -> str:
        return v.upper()


class MaterialUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    detail: Optional[str] = None
    unit: Optional[str] = None
    group_id: Optional[int] = None
