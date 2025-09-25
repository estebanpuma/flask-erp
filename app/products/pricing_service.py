# app/services/pricing_service.py
from decimal import Decimal

from sqlalchemy import func

from ..finance.tax_service import TaxService
from ..materials.models import MaterialLot
from .models import ProductDesign, ProductPriceHistory, ProductVariantMaterialDetail
from .price_entity import PricingEntity


class PricingService:
    def __init__(self, db_session):
        self.db = db_session
        self.labor_rate = 4
        self.overhead_rate = 3
        self.default_markup = 0.3
        self.tax_svc = TaxService(self.db)

    def _gather_costs(self, design: ProductDesign):
        """
        Retorna:
        - material_cost_unitario_promedio: (∑ lot.unit_cost * lot.quantity) / ∑ lot.quantity
        sobre todos los materiales usados en las variantes activas del diseño.
        - total_labor_hours: suma de standar_time de cada variante.
        """
        # 1) IDs de variantes
        variant_ids = [v.id for v in design.variants]
        if not variant_ids:
            return Decimal("0.00"), Decimal("0.00")

        session = self.db.session

        # 2) Subquery: para cada material_id agregado sobre las variantes,
        #    suma num = ∑(unit_cost * quantity), den = ∑(quantity)
        subq = (
            session.query(
                ProductVariantMaterialDetail.material_id.label("mat_id"),
                func.sum(MaterialLot.unit_cost * MaterialLot.quantity).label("num"),
                func.sum(MaterialLot.quantity).label("den"),
            )
            .join(
                MaterialLot,
                MaterialLot.material_id == ProductVariantMaterialDetail.material_id,
            )
            .filter(
                ProductVariantMaterialDetail.variant_id.in_(variant_ids),
                MaterialLot.quantity > 0,
            )
            .group_by(ProductVariantMaterialDetail.material_id)
            .subquery()
        )

        # 3) Costo promedio total: ∑(num/den) entre todos los materiales
        total_material_cost = session.query(
            func.coalesce(func.sum(subq.c.num / subq.c.den), 0)
        ).scalar()

        # 4) Mano de obra total
        total_labor_hours = sum(
            Decimal(str(v.standar_time or 0)) for v in design.variants
        )

        return Decimal(str(total_material_cost)), total_labor_hours

    def calculate_price(
        self,
        design_id: int,
        override_markup_pct=None,
        include_tax=False,
        force_recalc=False,
    ):
        # ya no hay with self.db.begin()
        design = self.db.query(ProductDesign).get(design_id)
        if not design:
            raise ValueError(f"Design {design_id} no existe")

        # Override manual
        if design.use_manual_price and not force_recalc:
            price_net = design.manual_price
            design.current_price = price_net

            ph = ProductPriceHistory(
                design_id=design.id,
                direct_cost=Decimal("0"),
                indirect_cost=Decimal("0"),
                markup_pct=Decimal("0"),
                price_net=price_net,
                override=True,
            )
            self.db.add(ph)
            self.db.flush()  # Opcional, si luego dependes de que el flush ocurra

            result = {"price_net": price_net, "is_override": True}
            # cálculo de impuestos...
            return result

        # Cálculo automático
        mat_cost, labor_h = self._gather_costs(design)
        markup = override_markup_pct or self.default_markup

        entity = PricingEntity(
            mat_cost, labor_h, self.labor_rate, self.overhead_rate, markup
        )
        net = entity.net_price
        design.current_price = net

        ph = ProductPriceHistory(
            design_id=design.id,
            direct_cost=entity.direct_cost,
            indirect_cost=entity.indirect_cost,
            markup_pct=markup,
            price_net=net,
            override=False,
        )
        self.db.add(ph)
        # No commit aquí: lo hará el caller

        result = {
            "price_net": net,
            "direct_cost": entity.direct_cost,
            "indirect_cost": entity.indirect_cost,
            "markup_pct": markup,
        }

        return result

    @staticmethod
    def create_price(data):
        """
        Método estático para usar directamente desde BasePostResource.
        data es el dict recibido del frontend.
        """
        from app import db

        from .dto_pricing import PricingRequestDTO

        with db.session.begin():
            payload = PricingRequestDTO(data)
            svc = PricingService(db.session)
            return svc.calculate_price(
                design_id=payload.design_id,
                override_markup_pct=payload.override_markup_pct,
                include_tax=payload.include_tax or False,
            )
