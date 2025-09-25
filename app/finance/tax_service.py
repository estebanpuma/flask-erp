# app/services/tax_service.py

from datetime import date
from decimal import Decimal

from .models import TaxRate


class TaxService:
    def __init__(self, session):
        self.session = session

    def _get_rate(self, code: str = None, on_date: date = None) -> Decimal:
        """Devuelve la tasa activa más reciente para un código en una fecha dada."""
        on = on_date or date.today()
        q = self.session.query(TaxRate.rate).filter(
            TaxRate.is_active, TaxRate.effective_date <= on
        )
        if code:
            q = q.filter(TaxRate.code == code)
        # ordena por fecha para tomar la más reciente
        rate = q.order_by(TaxRate.effective_date.desc()).limit(1).scalar()
        return Decimal(str(rate)) if rate is not None else Decimal("0")

    def calculate_tax(
        self, net_amount: Decimal, code: str = None, on_date: date = None
    ) -> Decimal:
        rate = self._get_rate(code, on_date)
        return (net_amount * rate).quantize(Decimal("0.01"))

    def calculate_gross(
        self, net_amount: Decimal, code: str = None, on_date: date = None
    ) -> Decimal:
        tax = self.calculate_tax(net_amount, code, on_date)
        return (net_amount + tax).quantize(Decimal("0.01"))
