from pydantic import BaseModel, Field
from typing import Optional, Literal


class LineCreateDTO(BaseModel):
    code: str = Field(..., min_length=1, max_length=10, strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = None
    

class LineUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SublineCreateDTO(BaseModel):
    code: str = Field(..., min_length=1, max_length=10, strip_whitespace=True)
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = None
    

class SublineUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None



class CollectionCreateDTO(BaseModel):
    
    line_id: int = Field(..., gt=0)
    subline_id: Optional[int] = None
    target_id: int = Field(None, gt=0)
    name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    description: Optional[str] = None
    

class CollectionUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None