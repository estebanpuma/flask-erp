from typing import List, Optional

from pydantic import Field, field_validator

from ..core.dto_base import MyBase


class InlineMaterialsDTO(MyBase):
    """DTO para un material dentro de la lista de materiales del producto."""

    material_id: int = Field(..., gt=0, alias="id")
    quantity: float = Field(..., ge=0)


class InlineVariantDTO(MyBase):
    """DTO para una variante dentro de la lista de variantes del producto."""

    size_id: int = Field(..., gt=0)


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

    @field_validator("subline_id")
    def empty_str_to_none(cls, v):
        """Convierte un string vacío a None antes de la validación."""
        if v == "":
            return None
        return v


class ProductPatchDTO(MyBase):
    """DTO que actualiza el producto. Usa Pydantic para validar campos opcionales."""

    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    old_code: Optional[str] = None
    line_id: Optional[int] = Field(None, gt=0)
    subline_id: Optional[int] = Field(None, gt=0)
    lifecycle_status: Optional[str] = None

    @field_validator("subline_id")
    def empty_str_to_none(cls, v):
        """Convierte un string vacío a None antes de la validación."""
        if v == "":
            return None
        return v


class ProductVariantCreateDTO(MyBase):
    """DTO para la creación de variantes de producto."""

    design_id: int = Field(..., gt=0)
    sizes_ids: List[int] = Field(..., min_length=1)


class ProductVariantPatchDTO(MyBase):
    """DTO para actualizar una variante de producto."""

    barcode: Optional[str] = None
    lifecycle_status: Optional[str] = None


class ProductVariantMaterialDetailDTO(MyBase):
    """DTO para la creación de un detalle de material de variante de producto."""

    material_id: int = Field(..., gt=0)
    quantity: float = Field(..., ge=0)


class VariantMaterialsCreateDTO(MyBase):
    """DTO para la creación de materiales de variante de producto"""

    variant_id: int = Field(..., gt=0)
    materials: List[ProductVariantMaterialDetailDTO]


class ProductVariantMaterialDetailPatchDTO(MyBase):
    """DTO para actualizar un detalle de material de variante de producto."""

    material_id: Optional[int] = Field(None, gt=0)
    quantity: Optional[float] = Field(None, gt=0)


# --- DTOs antiguos que podrían ser eliminados o refactorizados si ya no se usan ---
# He mantenido ProductDesignCreateDTO por si lo usas en otro lugar, pero lo he adaptado a Pydantic.
# Si no se usa, puedes eliminarlo.
class ProductDesignCreateDTO(MyBase):
    """DTO para crear/validar diseno."""

    product_id: int = Field(..., gt=0)
    name: Optional[str] = None
    description: Optional[str] = None
    color_ids: List[int] = Field(..., min_length=1)
    variants: List[InlineVariantDTO]
    materials: List[InlineMaterialsDTO]


class ProductDesignPatchDTO(MyBase):
    """DTO para actualizar un diseño de producto."""

    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    color_ids: Optional[List[int]] = Field(None, min_length=1)
    lifecycle_status: Optional[str] = None


class ProductDesignImageDTO(MyBase):
    """DTO para crear Imagenes de disenos/colores"""

    media_ids: List[int] = Field(..., min_length=1)
    is_primary: Optional[bool] = True
    order: Optional[int] = None
    design_id: int = Field(..., gt=0)
