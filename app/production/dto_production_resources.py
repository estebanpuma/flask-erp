from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Literal
from datetime import date
from ..core.dto_base import MyBase
from decimal import Decimal


class ProductionResourceDTO(MyBase):
    name:               str
    operation_id:       Optional[int]=None
    description:        Optional[str]=None
    kind:               Literal['labor', 'machine', 'tool']
    qty:                int 
    efficiency:         Optional[Decimal]=1
    setup_min:          Optional[Decimal]=0




class ProductionResourcePatchDTO(MyBase):
    name:               Optional[str]=None
    description:        Optional[str]=None
    kind:               Optional[Literal['labor', 'machine', 'tool']]=None  
    is_active:          Optional[bool]=None
    qty:                Optional[int]=None
    efficiency:         Optional[Decimal]=None
    setup_min:          Optional[Decimal]=None


class ProductionResourceStatusDTO(MyBase):
    is_active: bool



class VariantResourceUsageDTO(MyBase):
    
    variant_ids:        List[int] 
    resource_id:        int
    operation_id:       int
    std_min_unit:       Decimal


class VariantResourceUsagePatchDTO(MyBase):
    
    std_min_unit:       Decimal