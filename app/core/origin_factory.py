from ..sales.models import SaleOrder

from .exceptions import NotFoundError
from ..core.enums import ProductionSourceTypeEnum


class OriginFactory:
    
    ORIGIN_MAP = {
        ProductionSourceTypeEnum.SALES.value: SaleOrder,
        #"rd_order": RDOrder,
        #"stock_order": StockOrder
        # futuros: 'demo_order', 'urgent_order', etc.
    }

    @staticmethod
    def get_origin(origin_type, origin_id):
        model = OriginFactory.ORIGIN_MAP.get(origin_type)
        if not model:
            raise ValueError(f"Tipo de origen no soportado: {origin_type}")
        origin = model.query.get(origin_id)
        if not origin:
            raise NotFoundError(f"{origin_type} con ID {origin_id} no encontrado.")
        return origin