# validations/sales_validations.py
from ..core.enums import OrderStatus
from app.core.exceptions import ValidationError

def validate_sale_order_data(data):
    required_fields = ['order_number', 'order_date', 'status', 'client_id', 'sales_person_id', 'order_products']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Falta el campo requerido: {field}")

    if data['status'] not in [s.value for s in OrderStatus]:
        raise ValueError(f"Estado inválido: {data['status']}")

    if not isinstance(data['order_products'], list) or len(data['order_products']) == 0:
        raise ValidationError("Debe agregar al menos un producto al pedido.")
