
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class JobCreateDTO(BaseModel):
    code: str = Field(..., min_length=1, max_length=10, strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = None
    

class JobUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None