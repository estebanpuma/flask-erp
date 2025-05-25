from datetime import datetime
from ..core.exceptions import ValidationError

def parse_str(value, field=None, nullable=False, default=None):
    if value is None or str(value).strip().lower() in ["", "none", "nan"]:
        if nullable:
            return None
        if default is not None:
            return str(default)
        raise ValidationError(f"El campo '{field}' es obligatorio.")
    return str(value).strip()


def parse_int(value, field=None, nullable=False, min_value=None, max_value=None, default=None):
    if value is None or str(value).lower() in ["none", "nan", ""]:
        if nullable:
            return None
        if default is not None:
            value = default
        else:
            raise ValidationError(f"El campo '{field}' es obligatorio.")
    try:
        value = int(float(value))
    except (ValueError, TypeError):
        raise ValidationError(f"El campo '{field}' debe ser un número entero.")
    
    if min_value is not None and value < min_value:
        raise ValidationError(f"El campo '{field}' debe ser mayor o igual a {min_value}.")
    if max_value is not None and value > max_value:
        raise ValidationError(f"El campo '{field}' debe ser menor o igual a {max_value}.")
    
    return value


def parse_float(value, field=None, nullable=False, min_value=None, max_value=None, default=None):
    if value is None or str(value).lower() in ["none", "nan", ""]:
        if nullable:
            return None
        if default is not None:
            value = default
        else:
            raise ValidationError(f"El campo '{field}' es obligatorio.")
    try:
        value = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"El campo '{field}' debe ser un número decimal.")

    if min_value is not None and value < min_value:
        raise ValidationError(f"El campo '{field}' debe ser mayor o igual a {min_value}.")
    if max_value is not None and value > max_value:
        raise ValidationError(f"El campo '{field}' debe ser menor o igual a {max_value}.")
    
    return value


def parse_bool(value, field=None, default=None):
    if isinstance(value, bool):
        return value
    if value is None:
        if default is not None:
            return default
        raise ValidationError(f"El campo '{field}' es obligatorio.")
    value = str(value).strip().lower()
    if value in ['true', '1', 'yes', 'y', 'si']:
        return True
    elif value in ['false', '0', 'no', 'n']:
        return False
    raise ValidationError(f"El campo '{field}' debe ser un valor booleano válido (true/false).")


def parse_enum(value, enum_class, field=None, nullable=False, default=None):
    if value is None or str(value).strip().lower() in ["", "none", "nan"]:
        if nullable:
            return None
        if default is not None:
            value = default
        else:
            raise ValidationError(f"El campo '{field}' es obligatorio.")
    value_str = str(value).lower()
    for member in enum_class:
        if value_str == member.name.lower() or value_str == member.value.lower():
            return member
    raise ValidationError(f"El campo '{field}' no es válido. Opciones válidas: {[e.value for e in enum_class]}")


def parse_date(value, field=None, nullable=False, default=None):
    if value is None or str(value).lower() in ["", "none", "nan"]:
        if nullable:
            return None
        if default is not None:
            return default
        raise ValidationError(f"El campo '{field}' es obligatorio.")
    try:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        raise ValidationError(f"El campo '{field}' debe tener el formato YYYY-MM-DD.")



def parse_phone(value, field=None,):
    val = parse_str(value)
    if val and val.endswith(".0"):
        val = val[:-2]
    return val


def parse_ruc_or_ci(value):
    val = parse_str(value)
    if val and val.endswith(".0"):
        val = val[:-2]
    return val


