import re


def validate_client_data(data: dict):
    errors = {}
    required_fields = [
        'ruc_or_ci', 'name', 'client_type',
        'address', 'email', 'province_id', 'canton_id'
    ]

    # Validar campos requeridos
    for field in required_fields:
        if not data.get(field):
            errors[field] = f"El campo '{field}' es obligatorio."

    # Validar RUC o CI
    ruc_or_ci = data.get("ruc_or_ci")
    if ruc_or_ci and not validate_ruc_or_ci(ruc_or_ci):
        errors["ruc_or_ci"] = "El RUC o CI no es válido."
    else:
        if not validate_non_existing_ruc_or_ci(ruc_or_ci):
            errors['ruc_or_ci'] = "El RUC o CI ya existe en el sistema."

    #validar si Ruc o CI ya existen
    if not validate_non_existing_ruc_or_ci:
        errors["ruc_or_ci"] = "Ya existe un cliente con ese RUC o CI"

    # Validar email
    email = data.get("email")
    if email and not validate_email(email):
        errors["email"] = "El email no es válido."

    # Validar teléfono (opcional)
    phone = data.get("phone")
    if phone and not validate_phone(phone):
        errors["phone"] = "El número de teléfono no es válido."

    # Validar IDs
    try:
        data['province_id'] = int(data.get('province_id'))
        data['canton_id'] = int(data.get('canton_id'))
    except (ValueError, TypeError):
        errors['location'] = "province_id y canton_id deben ser enteros válidos."

    return errors


def validate_ruc_or_ci(ruc: str) -> bool:
    return bool(re.fullmatch(r"\d{10,13}", ruc))


def validate_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", email))


def validate_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"\d{7,10}$", phone))


def validate_non_existing_ruc_or_ci(ruc_or_ci: str) -> bool:
    """
    Verifica si un RUC o CI ya existe en la base de datos.
    
    Retorna:
        - True si NO existe (es válido para registrar).
        - False si YA existe (no se puede registrar).
    """
    from app.crm.models import Client

    existing_client = Client.query.filter_by(ruc_or_ci=ruc_or_ci).first()
    return existing_client is None

            
# app/crm/validations.py

def validate_client_partial_data(data: dict, instance) -> dict:
    errors = {}

    if 'ruc_or_ci' in data:
        if not isinstance(data['ruc_or_ci'], str) or len(data['ruc_or_ci']) not in [10, 13]:
            errors['ruc_or_ci'] = "El RUC o CI debe ser un string válido de 10 o 13 dígitos."
        elif not validate_non_existing_ruc_or_ci(data['ruc_or_ci']):
            errors['ruc_or_ci'] = "El RUC/CI ya está registrado."

    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name'].strip():
            errors['name'] = "El nombre no puede estar vacío."

    if 'email' in data:
        if not validate_email(data['email']):
            errors['email'] = "El email no es válido."

    if 'province_id' in data and not isinstance(data['province_id'], int):
        errors['province_id'] = "La provincia debe ser un número entero."

    if 'canton_id' in data and not isinstance(data['canton_id'], int):
        errors['canton_id'] = "El cantón debe ser un número entero."

    if 'phone' in data:
        if not isinstance(data['phone'], str) or not data['phone'].isdigit():
            errors['phone'] = "El teléfono debe ser un número válido."

    return errors
