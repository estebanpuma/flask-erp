from app import db

from ..core.enums import ProductionSourceTypeEnum
from ..core.exceptions import AppError, NotFoundError, ValidationError
from ..core.filters import apply_filters
from .models import ProductionRequest


class ProductionRequestServices:

    @staticmethod
    def get_obj(id):
        request = ProductionRequest.query.get(id)
        if not request:
            raise NotFoundError(f"No existe un requerimiento con el id: {id}")

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductionRequest, filters)

    @staticmethod
    def create_production_request(
        origin_type: str,
        origin_id: int,
        title: str,
        purpose: str = None,
        notes: str = None,
    ):

        if not ProductionSourceTypeEnum.has_value(origin_type):
            raise ValidationError(
                f"El origen del requerimiento: {origin_type} no es valido"
            )

        if origin_type == ProductionSourceTypeEnum.SALES.value:
            from ..sales.services import SalesOrderService

            sale = SalesOrderService.get_obj(origin_id)
            if not sale:
                raise ValidationError(
                    f"No existe una orden de venta con el id: {origin_id}"
                )

        if origin_type == ProductionSourceTypeEnum.STOCK.value:

            raise AppError("En construccion")

        if origin_type == ProductionSourceTypeEnum.RDI.value:
            raise AppError("En construccion")

        new_request = ProductionRequest(
            origin_type=origin_type,
            origin_id=origin_id,
            title=title,
            purpose=purpose,
            notes=notes,
        )

        db.session.add(new_request)

        return new_request
