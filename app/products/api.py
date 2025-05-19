from flask_restful import Api

from flask import Blueprint

from .resources import SizeDeleteResource, SizeGetResource, SizePostResource
from .resources import SeriesDeleteResource, SeriesGetResource, SeriesPatchResource, SeriesPostResource
from .resources import ColorDeleteResource, ColorGetResource, ColorPatchResource, ColorPostResource
from .resources import ProductDeleteResource, ProductGetResource, ProductPatchResource, ProductPostResource
from .resources import ProductVariantMaterialDeleteResource, ProductVariantMaterialListResource, ProductVariantMaterialPostResource, ProductVariantMaterialPatchResource
from .resources import (
    ProductVariantGetResource,
    ProductVariantListResource,
    ProductVariantPostResource,
    ProductVariantPatchResource,
    ProductVariantDeleteResource,
)

from .resources import ProductVariantImagePostResource, ProductVariantImageDeleteResource, ProductVariantImageGetResource

from . import products_bp

products_api_bp = Blueprint('products_api', __name__, url_prefix='/api/v1')

products_api = Api(products_api_bp)

#*******************************Products****************************************
#*****************************************************************************

products_api.add_resource(ProductGetResource, '/products', '/products/<int:resource_id>')
products_api.add_resource(ProductPostResource, '/products')
products_api.add_resource(ProductPatchResource, '/products/<int:resource_id>')
products_api.add_resource(ProductDeleteResource, '/products/<int:resource_id>')


#***************************ProductVAriant***************************************
#*******************************************************************************/*
products_api.add_resource(ProductVariantGetResource, "/product-variants", "/product-variants/<int:resource_id>")
products_api.add_resource(ProductVariantListResource, "/products/<int:product_id>/variants")
products_api.add_resource(ProductVariantPostResource, "/product-variants")
products_api.add_resource(ProductVariantPatchResource, "/product-variants/<int:resource_id>")
products_api.add_resource(ProductVariantDeleteResource, "/product-variants/<int:resource_id>")


#***************************VariantMaterials********************************
#****************************************************************************
products_api.add_resource(ProductVariantMaterialListResource, "/variant-materials", "/variant-materials/<int:resource_id>")
products_api.add_resource(ProductVariantMaterialPostResource, "/variant-materials")
products_api.add_resource(ProductVariantMaterialPatchResource, "/variant-materials/<int:resource_id>")
products_api.add_resource(ProductVariantMaterialDeleteResource, "/variant-materials/<int:resource_id>")


#*******************************VarianImages***********************************
#*******************************************************************************
#products_api.add_resource(ProductVariantImagePatchResource, '/product-variants/<int:variant_id>/images')
products_api.add_resource(ProductVariantImagePostResource, '/product-variants/<int:variant_id>/images')
products_api.add_resource(ProductVariantImageGetResource, '/product-variants/<int:variant_id>/images')
products_api.add_resource(ProductVariantImageDeleteResource, '/variant-images/<int:image_id>')

#*******************************sizes****************************************
#*****************************************************************************

products_api.add_resource(SizeGetResource, '/sizes', '/sizes/<int:resource_id>')
products_api.add_resource(SizePostResource, '/sizes')

products_api.add_resource(SizeDeleteResource, '/sizes/<int:resource_id>')


#*******************************sseries****************************************
#*****************************************************************************

products_api.add_resource(SeriesGetResource, '/series', '/series/<int:resource_id>')
products_api.add_resource(SeriesPostResource, '/series')
products_api.add_resource(SeriesPatchResource, '/series/<int:resource_id>')
products_api.add_resource(SeriesDeleteResource, '/series/<int:resource_id>')


#*******************************COlors****************************************
#*****************************************************************************


products_api.add_resource(ColorGetResource, '/colors', '/colors/<int:resource_id>')
products_api.add_resource(ColorPostResource, '/colors')
products_api.add_resource(ColorPatchResource, '/colors/<int:resource_id>')
products_api.add_resource(ColorDeleteResource, '/colors/<int:resource_id>')