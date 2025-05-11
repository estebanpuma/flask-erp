# validations/sales_validations.py
from ..core.enums import OrderStatus

def validate_sale_order_data(data):
    required_fields = ['order_number', 'order_date', 'status', 'client_id', 'sales_person_id', 'order_products']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Falta el campo requerido: {field}")

    if data['status'] not in [s.value for s in OrderStatus]:
        raise ValueError(f"Estado inválido: {data['status']}")

    for i, item in enumerate(data['order_products']):
        if 'product_id' not in item or 'qty' not in item or 'price' not in item:
            raise ValueError(f"El producto #{i+1} debe tener product_id, qty y price.")
