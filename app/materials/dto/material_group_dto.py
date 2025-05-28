# dto/material_group_dto.py
from pydantic import BaseModel, Field
from typing import Optional


class MaterialGroupCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = None


class MaterialGroupUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, max_length=100, strip_whitespace=True)
    description: Optional[str] = None
