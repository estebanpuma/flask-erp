from flask import Blueprint
from flask_restful import Api

from .resources import (
    CollectionGetResource,
    CollectionGetSpecificResource,
    CollectionPatchResource,
    CollectionPostResource,
    ColorDeleteResource,
    ColorGetResource,
    ColorPatchResource,
    ColorPostResource,
    LastPatchResource,
    LastsGetResource,
    LastSyncResource,
    LastTypeGetResource,
    LastTypePatchResource,
    LineDeleteResource,
    LineGetResource,
    LinePatchResource,
    LinePostResource,
    NextCodeCollectionCodeResource,
    NextProductCodeGetResource,
    ProductDeleteResource,
    ProductDesignDeleteResource,
    ProductDesignGetResource,
    ProductDesignPatchResource,
    ProductDesignPostResource,
    ProductGetResource,
    ProductPatchResource,
    ProductPostResource,
    ProductVariantDeleteResource,
    ProductVariantGetResource,
    ProductVariantImageDeleteResource,
    ProductVariantImageGetResource,
    ProductVariantImagePostResource,
    ProductVariantListResource,
    ProductVariantMaterialDeleteResource,
    ProductVariantMaterialListResource,
    ProductVariantMaterialPatchResource,
    ProductVariantMaterialPostResource,
    ProductVariantPatchResource,
    ProductVariantPostResource,
    SeriesDeleteResource,
    SeriesGetResource,
    SerieSizesGetReosurce,
    SeriesPatchResource,
    SeriesPostResource,
    SizeDeleteResource,
    SizeGetResource,
    SizePostResource,
    SublineDeleteResource,
    SubLineGetResource,
    SubLinePatchResource,
    SubLinePostResource,
    TargetGetResource,
    VariantMaterialsGetResource,
)

products_api_bp = Blueprint("products_api", __name__, url_prefix="/api/v1")

products_api = Api(products_api_bp)


# *******************************Lines/Sublines/Target/Collections****************************************
# *****************************************************************************

products_api.add_resource(
    LineGetResource, "/product-lines", "/product-lines/<int:resource_id>"
)
products_api.add_resource(LinePostResource, "/product-lines")
products_api.add_resource(LinePatchResource, "/product-lines/<int:resource_id>")

products_api.add_resource(
    SubLineGetResource, "/product-sublines", "/product-sublines/<int:resource_id>"
)

products_api.add_resource(LineDeleteResource, "/product-lines/<int:resource_id>")

products_api.add_resource(SubLinePostResource, "/product-sublines")
products_api.add_resource(SubLinePatchResource, "/product-sublines/<int:resource_id>")
products_api.add_resource(SublineDeleteResource, "/product-sublines/<int:resource_id>")


products_api.add_resource(
    TargetGetResource, "/product-targets", "/product-targets/<int:resource_id>"
)

products_api.add_resource(
    CollectionGetResource,
    "/product-collections",
    "/product-collections/<int:resource_id>",
)
products_api.add_resource(
    CollectionGetSpecificResource,
    "/product-collections/specific",
    "/product-collections/specific/<int:resource_id>",
)
products_api.add_resource(CollectionPostResource, "/product-collections")
products_api.add_resource(
    CollectionPatchResource, "/product-collections/<int:resource_id>"
)

products_api.add_resource(
    NextCodeCollectionCodeResource, "/product-collections/preview-code"
)

# ---------------------------Lasts---------------------------------------
products_api.add_resource(LastsGetResource, "/lasts", "/lasts/<int:resource_id>")
products_api.add_resource(LastPatchResource, "/lasts/<int:resource_id>/edit")
products_api.add_resource(LastSyncResource, "/lasts/sync")

products_api.add_resource(
    LastTypeGetResource, "/last-types", "/last-types/<int:resource_id>"
)
products_api.add_resource(LastTypePatchResource, "/last-types/<int:resource_id>/edit")

# *******************************Products****************************************
# *****************************************************************************

products_api.add_resource(
    ProductGetResource, "/products", "/products/<int:resource_id>"
)
products_api.add_resource(ProductPostResource, "/products")
products_api.add_resource(ProductPatchResource, "/products/<int:resource_id>")
products_api.add_resource(ProductDeleteResource, "/products/<int:resource_id>")

products_api.add_resource(NextProductCodeGetResource, "/products/next-code")


# *******************************ProductDesigns****************************************
# *****************************************************************************

products_api.add_resource(
    ProductDesignGetResource, "/product-designs", "/product-designs/<int:resource_id>"
)
products_api.add_resource(ProductDesignPostResource, "/product-designs")
products_api.add_resource(
    ProductDesignPatchResource, "/product-designs/<int:resource_id>"
)
products_api.add_resource(
    ProductDesignDeleteResource, "/product-designs/<int:resource_id>"
)


# ***************************ProductVAriant***************************************
# *******************************************************************************/*
products_api.add_resource(
    ProductVariantGetResource,
    "/product-variants",
    "/product-variants/<int:resource_id>",
)
products_api.add_resource(
    ProductVariantListResource, "/products/<int:product_id>/variants"
)
products_api.add_resource(ProductVariantPostResource, "/product-variants")
products_api.add_resource(
    ProductVariantPatchResource, "/product-variants/<int:resource_id>"
)
products_api.add_resource(
    ProductVariantDeleteResource, "/product-variants/<int:resource_id>"
)


# ***************************VariantMaterials********************************
# ****************************************************************************
products_api.add_resource(
    ProductVariantMaterialListResource,
    "/variant-materials",
    "/variant-materials/<int:resource_id>",
)
products_api.add_resource(ProductVariantMaterialPostResource, "/variant-materials")
products_api.add_resource(
    ProductVariantMaterialPatchResource, "/variant-materials/<int:resource_id>"
)
products_api.add_resource(
    ProductVariantMaterialDeleteResource, "/variant-materials/<int:resource_id>"
)
products_api.add_resource(
    VariantMaterialsGetResource, "/variant/<int:resource_id>/materials"
)


# *******************************VarianImages***********************************
# *******************************************************************************
# products_api.add_resource(ProductVariantImagePatchResource, '/product-variants/<int:variant_id>/images')
products_api.add_resource(
    ProductVariantImagePostResource, "/product-variants/<int:variant_id>/images"
)
products_api.add_resource(
    ProductVariantImageGetResource, "/product-variants/<int:variant_id>/images"
)
products_api.add_resource(
    ProductVariantImageDeleteResource, "/variant-images/<int:image_id>"
)

# *******************************sizes****************************************
# *****************************************************************************

products_api.add_resource(SizeGetResource, "/sizes", "/sizes/<int:resource_id>")
products_api.add_resource(SizePostResource, "/sizes")

products_api.add_resource(SizeDeleteResource, "/sizes/<int:resource_id>")


products_api.add_resource(SerieSizesGetReosurce, "/series/<int:resource_id>/sizes")
# *******************************sseries****************************************
# *****************************************************************************

products_api.add_resource(SeriesGetResource, "/series", "/series/<int:resource_id>")
products_api.add_resource(SeriesPostResource, "/series")
products_api.add_resource(SeriesPatchResource, "/series/<int:resource_id>")
products_api.add_resource(SeriesDeleteResource, "/series/<int:resource_id>")


# *******************************COlors****************************************
# *****************************************************************************


products_api.add_resource(ColorGetResource, "/colors", "/colors/<int:resource_id>")
products_api.add_resource(ColorPostResource, "/colors")
products_api.add_resource(ColorPatchResource, "/colors/<int:resource_id>")
products_api.add_resource(ColorDeleteResource, "/colors/<int:resource_id>")
