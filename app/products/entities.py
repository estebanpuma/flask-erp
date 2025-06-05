
from .models import Product, ProductDesign, ProductVariant, ProductVariantMaterialDetail
from ..core.exceptions import ValidationError
from ..common.parsers import parse_str, parse_int, parse_float

class ProductEntity:
    '''Entidad para producto'''
    def __init__(self, data: dict):
        self.code = parse_str(data.get("code"), field="code")
        self.name = parse_str(data.get("name"), field="name")
        self.description = data.get("description")
        self.line_id = parse_int(data.get("line_id"), field="line_id", nullable=True)
        self.sub_line_id = parse_int(data.get("sub_line_id"), field="sub_line_id", nullable=True)
        self.designs = []  # para adjuntar diseños si se desea construir como agregado


    def to_model(self):
        return Product(
            code=self.code,
            name=self.name,
            description=self.description,
            line_id=self.line_id,
            sub_line_id=self.sub_line_id
        )
    
class PatchProductEntity:
    """Entidad que actualiza el producto"""
    
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
            instance.name = self.name
        if self.description:
            instance.description = self.description
        if self.line_id:
            instance.line_id = self.line_id
        if self.sub_line_id:
            instance.sub_line = self.sub_line_id
        return instance


class ProductDesignEntity:
    """Entidad para crear diseno"""
    def __init__(self, data: dict):
        #input
        self.product_id = parse_int(data.get("product_id"), field="product_id")
        self.name = parse_str(data.get('name'), field='name', nullable=True)
        self.description = data.get("description")
        self.color_ids = data.get("color_ids", [])
        self.series_ids = data.get("series_ids", [])
        #Service
        self.product_code = parse_str(data.get("product_code"), field='product_code')  # Proveído por el servicio
        self.color_codes = data.get("color_codes")  # Proveído por el servicio
        
        self._generate_code()
        self._validate()
        

    def _generate_code(self):
        """Genera C001NE (producto + colores)"""
        print(f'color codes: {self.color_codes}')
        colors_codes = [c.upper() for c in self.color_codes]
        color_part = "".join(colors_codes)
        self.code = f"{self.product_code}{str(color_part)}"


    def _validate(self):
        if not self.product_id:
            raise ValidationError("product_id es obligatorio.")
        if not isinstance(self.color_ids, list):
            raise ValidationError("color_ids debe ser una lista.")
        if not isinstance(self.series_ids, list) or not self.series_ids:
            raise ValidationError("serie_ids debe ser una lista con al menos un valor.")
        if not self.color_ids:
            raise ValidationError("Debe tener al menos un color.")
        

    def to_model(self):
        '''Retorna un modelo del producto'''
        return ProductDesign(
            product_id=self.product_id,
            code=self.code,
            name=self.name,
            description=self.description
        )


class ProductVariantEntity:
    def __init__(self, data: dict):
        #input
        self.design_id = parse_int(data.get("design_id"), field="design_id")
        self.size_id = parse_int(data.get("size_id"), field="size_id")
        self.barcode = parse_str(data.get("barcode"), field="barcode", nullable=True)
        self.stock = parse_float(data.get("stock", 0), field="stock", min_value=0)
        self.materials = data.get("materials", [])
        #Service
        self.design_code = parse_str(data.get("design_code"))  # Proveído por el servicio
        self.size_value = parse_str(data.get("size_value"))  # Proveído por el servicio
    
        self._generate_code()
        self._validate()

    def _generate_code(self):
        """Genera C001NE25 (diseño + talla)"""
        self.code = f"{self.design_code}{self.size_value}"

    def _validate(self):

        if not self.design_id or not self.size_id:
            raise ValidationError("design_id y size_id son obligatorios.")
        if not isinstance(self.materials, list) or not self.materials:
            raise ValidationError("Cada variante debe tener al menos una lista de materiales asociada.")

    def to_model(self):
        return ProductVariant(
            design_id=self.design_id,
            size_id=self.size_id,
            code=self.code,
            barcode=self.barcode,
            stock=self.stock
        )




class ProductVariantMaterialEntity:
    """Entidad para incluir un nuevo material a las variantes"""

    def __init__(self, data:dict):
        self.variant_id = parse_int(data.get('variant_id'))
        self.material_id = parse_int(data.get('material_id'))
        self.quantity = parse_float(data.get('quantity'))
        self._validate()

    def _validate(self):
        if self.quantity <= 0:
            raise ValidationError('No se pude ingresar una cantidad menor o igual a cero')
        
    def to_model(self)->ProductVariantMaterialDetail:
        return ProductVariantMaterialDetail(
            material_id = self.material_id,
            variant_id = self.variant_id,
            quantity = self.quantity
        )
