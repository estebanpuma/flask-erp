from app.core.exceptions import ValidationError

def validate_payment_method_data(data):
    required_fields = ['name']
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"El campo '{field}' es obligatorio.")



def validate_payment_method_patch_data(data):
    if not data:
        raise ValidationError("No se enviaron datos.")

    allowed = ['name', 'description']
    for key in data:
        if key not in allowed:
            raise ValidationError(f"Campo no permitido: {key}")

    if 'name' in data and not data['name'].strip():
        raise ValidationError("El campo 'name' no puede estar vacío.")