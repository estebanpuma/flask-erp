from pydantic import Field

from ..core.dto_base import MyBase


class ObjectCodePreviewDTO(MyBase):
    object_type: str = Field(..., min_length=1, max_length=50)
    prefix: str = Field(..., min_length=1, max_length=20)
