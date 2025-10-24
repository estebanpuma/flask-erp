# dto/material_group_dto.py
from typing import Optional

from pydantic import BaseModel, Field


class MaterialGroupCreateDTO(BaseModel):
    code: str
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = None


class MaterialGroupUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    description: Optional[str] = None


class MaterialSubGroupCreateDTO(BaseModel):
    material_group_id: int
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = None


class MaterialSubGroupUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    description: Optional[str] = None
    group_id: Optional[int] = None
