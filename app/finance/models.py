# app/models/tax_rate.py
from sqlalchemy import Boolean, Column, Date, Integer, Numeric, String

from ..common.models import BaseModel


class TaxRate(BaseModel):
    __tablename__ = "tax_rates"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(String(100), nullable=True)
    rate = Column(Numeric(5, 4), nullable=False)  # ej. 0.1200 = 12%
    is_active = Column(Boolean, nullable=False, default=True)
    effective_date = Column(Date, nullable=False)  # desde cuándo aplica
