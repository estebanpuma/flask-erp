from typing import Optional

from pydantic import BaseModel, Field


class WarehouseCreateDTO(BaseModel):
    code: str = Field(..., min_length=1, max_length=20, strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = None
    location: Optional[str] = None


class WarehouseUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
