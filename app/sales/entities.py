from datetime import datetime
from ..common.parsers import (
    parse_str, parse_date, parse_float, parse_int, parse_enum
)
from ..crm.services import CRMServices
from ..products.services import VariantService as ProductVariantService
from .models import OrderStatus
from ..core.exceptions import ValidationError
from ..admin.models import Salesperson


class SaleOrderLineEntity():
    def __init__(self, data: dict):
        self.variant_id = parse_int(data.get("variant_id"), field="variant_id")
        self.quantity = parse_int(data.get("quantity"), field="quantity", min_value=1)
        self.price_unit = parse_float(data.get("price_unit"), field="price_unit", min_value=0)
        self.discount = parse_float(data.get("discount", 0.0), field="discount", min_value=0)

        # Validación de existencia
        self.variant = ProductVariantService.get_obj(self.variant_id)

        if self.discount > self.price_unit:
            raise ValidationError("El descuento no puede ser mayor al precio unitario.")


class SaleOrderEntity():
    def __init__(self, data: dict):
        self.order_number = parse_str(data.get("order_number"), field="order_number", nullable=True)
        self.order_date = parse_date(data.get("order_date"), default=datetime.today())
        self.delivery_date = parse_date(data.get("delivery_date"), nullable=True)
        self.delivery_address = parse_str(data.get("delivery_address"), field="delivery_address", nullable=True)
        self.status = parse_enum(data.get("status", OrderStatus.DRAFT.value), OrderStatus, field="status")
        self.discount = parse_float(data.get("discount", 0.0), field="discount", min_value=0)
        self.tax = parse_float(data.get("tax", 0.0), field="tax", min_value=0)

        self.client_id = parse_int(data.get("client_id"), field="client_id")
        self.sales_person_id = parse_int(data.get("sales_person_id"), field="sales_person_id", nullable=True)

        self.client = CRMServices.get_obj(self.client_id)
        self.salesperson = None
        if self.sales_person_id:
            self.salesperson = Salesperson.query.get(self.sales_person_id)

        # Líneas (opcional en PATCH, obligatorio en POST)
        self.lines_data = data.get("lines")
        self.lines = []
        if self.lines_data:
            if not isinstance(self.lines_data, list):
                raise ValidationError("El campo 'lines' debe ser una lista.")
            seen_variants = set()
            for line_data in self.lines_data:
                line_entity = SaleOrderLineEntity(line_data)

                if line_entity.variant_id in seen_variants:
                    raise ValidationError(f"La variante con ID {line_entity.variant_id} está repetida en las líneas.")
                seen_variants.add(line_entity.variant_id)

                self.lines.append(line_entity)


        # Validación de fechas
        if self.delivery_date and self.delivery_date < self.order_date:
            raise ValidationError("La fecha de entrega no puede ser anterior a la fecha de la orden.")
