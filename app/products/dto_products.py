from typing import List, Optional

from pydantic import Field

from ..core.dto_base import MyBase
from .models import Product


class InlineMaterialsDTO(MyBase):
    """DTO para un material dentro de la lista de materiales del producto."""

    material_id: int = Field(..., gt=0, alias="id")
    quantity: float = Field(..., ge=0)


class InlineVariantDTO(MyBase):
    """DTO para una variante dentro de la lista de variantes del producto."""

    size_id: int = Field(..., gt=0)
    color_id: int = Field(..., gt=0)


class InlineColorDTO(MyBase):
    """DTO para un color dentro de la lista de colores del producto."""

    id: int = Field(..., gt=0)


class ProductCreateDTO(MyBase):
    """DTO validador para la creación de un producto completo."""

    name: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    description: Optional[str] = None
    old_code: Optional[str] = None
    line_id: int = Field(..., gt=0)
    subline_id: Optional[int] = Field(None, gt=0)
    target_id: int = Field(..., gt=0)
    collection_id: int = Field(
        ...,
    )
    colors: List[InlineColorDTO] = Field(..., min_length=1)
    media_ids: Optional[List[int]] = Field(
        [], description="Lista de IDs de MediaFile para asociar"
    )

    class Config:
        # Permite que Pydantic funcione con alias como 'id' en lugar de 'material_id'
        populate_by_name = True


class ProductPatchDTO(MyBase):
    """DTO que actualiza el producto. Usa Pydantic para validar campos opcionales."""

    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    old_code: Optional[str] = None
    line_id: Optional[int] = Field(None, gt=0)
    subline_id: Optional[int] = Field(None, gt=0)

    def apply_changes(self, instance: Product) -> Product:
        """Aplica los cambios del DTO a una instancia del modelo SQLAlchemy."""
        update_data = self.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(instance, key, value)
        return instance


# --- DTOs antiguos que podrían ser eliminados o refactorizados si ya no se usan ---
# He mantenido ProductDesignCreateDTO por si lo usas en otro lugar, pero lo he adaptado a Pydantic.
# Si no se usa, puedes eliminarlo.
class ProductDesignCreateDTO(MyBase):
    """DTO para crear/validar diseno (versión Pydantic)."""

    product_id: int = Field(..., gt=0)
    name: Optional[str] = None
    description: Optional[str] = None
    color_ids: List[int] = Field(..., min_length=1)
    variants: List[InlineVariantDTO]
    materials: List[InlineMaterialsDTO]
