from app.core.exceptions import ValidationError


def validate_payment_method_data(data):
    required_fields = ["name"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"El campo '{field}' es obligatorio.")


def validate_payment_method_patch_data(data, instance):
    if not data:
        raise ValidationError("No se enviaron datos.")

    allowed = ["name", "description"]
    for key in data:
        if key not in allowed:
            raise ValidationError(f"Campo no permitido: {key}")

    if "name" in data and not data["name"].strip():
        raise ValidationError("El campo 'name' no puede estar vacío.")


# payment_validations


def validate_payment_plan_data(data):
    required_fields = ["sale_order_id", "payment_method_id", "total_amount"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"El campo '{field}' es obligatorio.")

    if "total_amount" in data and data["total_amount"] <= 0:
        raise ValidationError("El monto total debe ser mayor a 0.")

    if "total_installments" in data:
        if (
            not isinstance(data["total_installments"], int)
            or data["total_installments"] < 1
        ):
            raise ValidationError(
                "El número de cuotas debe ser un entero mayor o igual a 1."
            )
