
def generate_variant_code(base_code: str, color_codes: list[str]) -> str:
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