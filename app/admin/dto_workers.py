
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class WorkerCreateDTO(BaseModel):
    ci: str = Field(..., min_length=1, max_length=10, strip_whitespace=True)
    first_name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    last_name: str = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    job_id: int = Field(..., gt=0)
    phone: Optional[str] = None
    hour_rate_normal: float = Field(1, gt=0)
    salary: float = Field(gt=0)
    worker_type: Literal['Planta', 'Rotativo', 'Comisión', 'Contratista']
    notes: Optional[str] = None

    @field_validator('ci')
    @classmethod
    def ci_must_be_numbers(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('La cédula debe contener solo números')
        if len(v) != 10:
            raise ValueError('La cédula debe tener exactamente 10 dígitos.')
        return v
    
    @field_validator('phone')
    @classmethod
    def hpone_must_be_numbers(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('EL telefono debe contener solo números')
        
    


class WorkerUpdateDTO(BaseModel):
    first_name: Optional[str] = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    last_name: Optional[str] = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    job_id: Optional[int] = Field(..., gt=0)
    hour_rate_normal: Optional[float] = Field(..., gt=0)
    salary: float = Field(gt=0)
    worker_type: Optional[Literal['Planta', 'Rotativo', 'Comisión' 'Contratista']] 
    is_active: Optional[bool] = True
    notes: Optional[str] = None
