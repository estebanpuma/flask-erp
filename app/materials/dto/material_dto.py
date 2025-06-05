# dto/material_dto.py
from pydantic import BaseModel, Field
from typing import Optional


class MaterialCreateDTO(BaseModel):
    code: str = Field(..., min_length=1, max_length=20, strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    detail: Optional[str] = None
    unit: Optional[str] = None
    group_id: Optional[int] = None


class MaterialUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    detail: Optional[str] = None
    unit: Optional[str] = None
    group_id: Optional[int] = None
