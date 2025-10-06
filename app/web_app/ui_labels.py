# app/web_app/ui_labels.py

# Este diccionario centraliza las etiquetas de la interfaz de usuario.
# Si necesitas cambiar "Línea" por "Tipo", solo lo cambias aquí.
UI_LABELS = {
    # Singular y Plural
    "line": "Línea",
    "lines": "Líneas",
    "subline": "Sublínea",
    "sublines": "Sublíneas",
    "collection": "Colección",
    "collections": "Colecciones",
    "targets": "Target",
    "target": "Target",
    "materials": "Materiales",
    "material": "Material",
    "colors": "Colores",
    "color": "Color",
    "sizes": "Tallas",
    "size": "Talla",
    "series": "Series",
    "serie": "Serie",
    "variants": "Variantes",
    "variant": "Variante",
    "designs": "Diseños",
    "design": "Diseño",
    "product": "Producto",
    "products": "Productos",
    "last": "Horma",
    "lasts": "Hormas",
    # Acciones y Títulos
    "new_line": "Nueva Línea",
    "new_subline": "Nueva Sublínea",
    "new_collection": "Nueva Colección",
    "new_product": "Nuevo Producto",
    "new_last": "Nueva Horma",
    "line_detail": "Detalle de Línea",
    "lines_title": "Líneas de productos",
    "sublines_title": "Sublíneas de productos",
    # Campos de formulario y tablas
    "line_name": "Nombre de la línea",
    "line_code": "Código de la línea",
    "code": "Código",
    "name": "Nombre",
    "description": "Descripción",
    "num_products": "Nº productos",
    "associated_products": "Productos asociados",
    # Mensajes
    "no_lines_registered": "No hay líneas registradas.",
    "no_sublines_registered": "No hay sublíneas registradas.",
    "no_lasts_registered": "No existen hormas registradas",
    "code_exists_error": "🚫 El código ya existe.",
    "without_code": "Sin código",
    "without_description": "Sin descripción",
}


def inject_ui_labels():
    """
    Hace que el diccionario UI_LABELS esté disponible en todas las plantillas Jinja2.
    """
    return dict(label=UI_LABELS)
