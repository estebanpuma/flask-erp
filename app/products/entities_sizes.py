from .models import SizeSeries, Size
from ..core.exceptions import ValidationError
from ..common.parsers import parse_str, parse_int, parse_float


class SeriesEntity:
    """Entidad de Series para creacion."""
    def __init__(self, data:dict):
        print(f'data inside entity: {data}')
        self.name = parse_str(data.get('name'), field='name').upper()
        self.start_size = parse_int(data.get('start_size'))
        self.end_size = parse_int(data.get('end_size'))
        self.category = parse_str(data.get('category'))
        self.description = parse_str(data.get('description'), nullable=True)

        self.validate()

    def validate(self):
       
        if self.start_size > self.end_size:
            raise ValidationError('La talla de inicio no puede ser mayor a la talla final')
        
        if self.start_size < 0:
            raise ValidationError('La talla de inicio no puede ser menor que 0')
        
    def to_model(self) -> SizeSeries:
        return SizeSeries(
            name = self.name,
            start_size = self.start_size,
            end_size = self.end_size,
            description = self.description,
            category = self.category
        )
    


class SeriesUpdateEntity:
    """Entidad solo para actualización con campos editables declarados."""
    # Campos permitidos para actualización
    EDITABLE_FIELDS = {"name", "description"}
    
    def __init__(self, data: dict):
        self.name = parse_str(data.get("name")) if "name" in data else None
        self.description = parse_str(data.get("description")) if "description" in data else None
        self._validate(data)

    def _validate(self, data: dict):
        # Valida que no se intenten editar campos no permitidos
        invalid_fields = set(data.keys()) - self.EDITABLE_FIELDS
        if invalid_fields:
            raise ValidationError(f"Campos no editables: {invalid_fields}")
        
        # Validaciones específicas de campos editables
    def apply_changes(self, instance: SizeSeries) -> SizeSeries:
        """Aplica solo los campos editables."""
        if self.name is not None:
            instance.name = self.name
        if self.description is not None:
            instance.description = self.description
        return instance
    



class SizesUpdateEntity:
    """Entidad solo para actualización con campos editables declarados."""
    # Campos permitidos para actualización
    EDITABLE_FIELDS = {"length", "width"}
    
    def __init__(self, data: dict):
        self.length = parse_float(data.get("length")) if "length" in data else None
        self.width = parse_float(data.get("width")) if "width" in data else None
        self._validate(data)

    def _validate(self, data: dict):
        # Valida que no se intenten editar campos no permitidos
        invalid_fields = set(data.keys()) - self.EDITABLE_FIELDS
        if invalid_fields:
            raise ValidationError(f"Campos no editables: {invalid_fields}")
        
        
        # Validaciones específicas de campos editables
    def apply_changes(self, instance: Size) -> Size:
        """Aplica solo los campos editables."""
        if self.length is not None:
            instance.length = self.length
        if self.width is not None:
            instance.width = self.width
        return instance