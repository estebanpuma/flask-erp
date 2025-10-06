from typing import Optional

from pydantic import Field

from ..core.dto_base import MyBase  # ← tu clase con validate_with_message


class LineCreateDTO(MyBase):
    code: str = Field(..., min_length=1, max_length=10, strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = None


class LineUpdateDTO(MyBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SublineCreateDTO(MyBase):
    code: str = Field(..., min_length=1, max_length=10, strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = None


class SublineUpdateDTO(MyBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CollectionCreateDTO(MyBase):
    line: int = Field(..., gt=0)
    subline: int = Field(..., gt=0)
    target: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    code: str = Field(..., min_length=1, max_length=10, strip_whitespace=True)
    description: Optional[str] = None


class CollectionUpdateDTO(MyBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
