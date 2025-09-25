# app/entities/pricing_entity.py

from decimal import Decimal


class PricingEntity:
    def __init__(
        self,
        material_cost: Decimal,
        labor_hours: Decimal,
        labor_rate: Decimal,
        overhead_rate: Decimal,
        markup_pct: Decimal,
    ):

        self.material_cost = material_cost
        self.labor_hours = labor_hours
        self.labor_rate = labor_rate
        self.overhead_rate = overhead_rate
        self.markup_pct = markup_pct

    @property
    def direct_cost(self) -> Decimal:
        return self.material_cost + (self.labor_hours * self.labor_rate)

    @property
    def indirect_cost(self) -> Decimal:
        return self.labor_hours * self.overhead_rate

    @property
    def net_price(self) -> Decimal:
        base = self.direct_cost + self.indirect_cost
        return base * (1 + self.markup_pct)
