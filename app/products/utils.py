def generate_design_code(base_code: str, color_codes: list[str]) -> str:
    """
    Genera un código único para la variante combinando el código del producto
    con los códigos de los colores, ordenados alfabéticamente.

    Ejemplo: base_code = "C001", color_codes = ["BL", "NE"] → "C001BLNE"
    """
    if not base_code or not isinstance(color_codes, list):
        raise ValueError("Código base y lista de colores son obligatorios.")

    clean_codes = [c.strip().upper() for c in color_codes if c]
    sorted_codes = sorted(clean_codes)
    return base_code.upper() + "".join(sorted_codes)


def generate_variant_code(base_code: str, size_value: str) -> str:
    """
    Genera un código único para la variante combinando el código del diseno
    con la talla

    Ejemplo: base_code = "C001NEBL", size_value = 38 → "C001BLNE38"
    """
    if not base_code or not size_value:
        raise ValueError("Código base y la talla son obligatorios.")

    return base_code.upper() + "".join(size_value)
