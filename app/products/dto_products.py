
from .models import Product, ProductDesign, ProductVariant, ProductVariantMaterialDetail
from ..core.exceptions import ValidationError
from ..common.parsers import parse_str, parse_int, parse_float, parse_ids_list

class ProductCreateDTO:
    '''DTO validador para producto'''
    def __init__(self, data: dict):
        self.name = parse_str(data.get("name"), field="Nombre")
        self.description = parse_str(data.get('description'), field='Descripcion', nullable=True)
        self.line_id = parse_int(data.get("line_id"), field="Linea")
        self.subline_id = parse_int(data.get("sub_line_id"), field="Sublinea", nullable=True)
        self.target_id = parse_int(data.get("target_id"), field="target")
        self.collection_id = parse_int(data.get("collection_id"), field="Coleccion")
        self.designs = [InlineProductDesignDTO(v) for v in data.get("designs", [])]
        self.variants = [InlineVariantDTO(v) for v in data.get("variants", [])]
        self.materials = [InlineMaterialsDTO(v) for v in data.get("materials", [])]


class ProductPatchDTO:
    """DTO que actualiza el producto"""
    
    EDITABLE_FIELDS = {'name', 'description', 'line_id', 'sub_line_id'}

    def __init__(self, data:dict):
        self.name = parse_str(data.get("name"), field="name", nullable=True)
        self.description = parse_str(data.get("description"), field='description', nullable=True)
        self.line_id = parse_int(data.get("line_id"), field="line_id", nullable=True)
        self.sub_line_id = parse_int(data.get("sub_line_id"), field="sub_line_id", nullable=True)
        self._validate(data)

    def _validate(self, data: dict):
        # Valida que no se intenten editar campos no permitidos
        invalid_fields = set(data.keys()) - self.EDITABLE_FIELDS
        if invalid_fields:
            raise ValidationError(f"Campos no editables: {invalid_fields}")

    def apply_changes(self, instance:Product)->Product:
        if self.name:
            if instance.name != self.name:
                instance.name = self.name
        if self.description:
            instance.description = self.description
        if self.line_id:
            instance.line_id = self.line_id
        if self.sub_line_id:
            instance.sub_line = self.sub_line_id
        return instance


class ProductDesignCreateDTO:
    """DTO para crear/validar diseno"""
    def __init__(self, data: dict):
        #input
        self.product_id = parse_int(data.get("product_id"), field="Id del producto")
        self.name = parse_str(data.get('name'), field='Nombre', nullable=True)
        self.description =  parse_str(data.get('description'), nullable=True)
        self.color_ids = [parse_ids_list(d.get('color_ids'), field='Id de colores(e:design)', min_value=1) for d in data.get('designs', [])] 
        self.variants = [InlineVariantDTO(v) for v in data.get("variants", [])] 
        self.materials = [InlineMaterialsDTO(v) for v in data.get("materials", [])]
    

class InlineProductDesignDTO:
    """DTO para crear/validar diseno"""
    def __init__(self, data: dict):
        self.name = parse_str(data.get('name'), field='Nombre', nullable=True)
        self.description =  parse_str(data.get('description'), nullable=True)
        self.color_ids = parse_ids_list(data.get('color_ids'), field='Id de colores', min_value=1)


class InlineVariantDTO:
    def __init__(self, data: dict):
        #input
        self.series_ids = parse_ids_list(data.get("series_ids"), field="Ids de serie", min_value=1)
    

class ProductVariantCreateDTO:
    def __init__(self, data: dict):
        #input
        self.design_id = parse_int(data.get("design_id"), field="design_id")
        self.series_ids = parse_ids_list(data.get("series_ids"), field="Ids de serie", min_value=1)
        self.materials = [InlineMaterialsDTO(v) for v in data.get("materials", [])]


class ProductVariantMaterialCreateDTO:
    """DTO para incluir un nuevo material a las variantes"""

    def __init__(self, data:dict):
        self.variant_id = parse_int(data.get('variant_id'), field='ID de variante')
        self.material_id = parse_int(data.get('id'), field='ID material')
        self.quantity = parse_float(data.get('quantity'), field='Cantidad de material')


class InlineMaterialsDTO:
    """DTO para incluir un nuevo material a las variantes general"""

    def __init__(self, data:dict):
        self.material_id = parse_int(data.get('id'), field='ID material')
        self.quantity = parse_float(data.get('quantity'), min_value=0, field='Cantidad de material')
