# utils/query_filters.py

from sqlalchemy.orm import Query
from sqlalchemy.orm.attributes import InstrumentedAttribute


def apply_filters(model, filters: dict, query_only: bool = None) -> list:
    """
    Aplica filtros dinámicos a un modelo SQLAlchemy basado en la convención campo__operador=valor.

    Ejemplos de uso:
        ?name__contains=juan             → name ILIKE '%juan%'
        ?ruc_or_ci=1234567890           → igualdad exacta
        ?code__in=BL,NE,RO              → code IN (...)
        ?active__neq=true               → active != True
        ?age__gte=18                    → age >= 18
    """

    SUPPORTED_OPERATORS = {
        "eq": lambda c, v: c == v,
        "neq": lambda c, v: c != v,
        "lt": lambda c, v: c < v,
        "lte": lambda c, v: c <= v,
        "gt": lambda c, v: c > v,
        "gte": lambda c, v: c >= v,
        "contains": lambda c, v: c.ilike(f"%{v}%"),
        "startswith": lambda c, v: c.ilike(f"{v}%"),
        "endswith": lambda c, v: c.ilike(f"%{v}"),
        "like": lambda c, v: c.like(v),
        "ilike": lambda c, v: c.ilike(v),
        "in": lambda c, v: c.in_(v.split(",")),
    }

    query: Query = model.query

    for raw_key, raw_value in filters.items():
        field_name, op = parse_filter_key(raw_key, SUPPORTED_OPERATORS)
        if not hasattr(model, field_name):
            continue

        column: InstrumentedAttribute = getattr(model, field_name)

        try:
            value = normalize_value(raw_value)
            filter_expr = SUPPORTED_OPERATORS[op](column, value)
            query = query.filter(filter_expr)
        except Exception as e:
            # En entorno real puedes loggear con current_app.logger.warning(...)
            print(f"Error al aplicar filtro {raw_key}={raw_value}: {e}")

    if query_only:
        return query
    return query.all()


def parse_filter_key(key: str, supported_ops: set) -> tuple[str, str]:
    """
    Extrae nombre de campo y operador desde la clave del filtro.
    Por ejemplo: 'name__contains' → ('name', 'contains')
    """
    if "__" in key:
        parts = key.rsplit("__", 1)
        if parts[1] in supported_ops:
            return parts[0], parts[1]
    return key, "eq"


def normalize_value(value: str):
    """
    Normaliza el valor de entrada (puedes ampliar para tipos como booleanos, fechas, etc.).
    """
    if isinstance(value, str):
        val = value.strip().upper()
        if val == "TRUE":
            return True
        if val == "FALSE":
            return False
        return value.strip()
    return value
