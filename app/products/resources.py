from flask import request

from flask_restful import marshal, Resource

from ..core.utils import success_response, error_response

from ..core.resources import BasePatchResource, BaseGetResource, BasePostResource, BaseDeleteResource

from ..common.services import ProductCodeGenerator, CollectionCodeGenerator

from .services import ProductService, ProductVariantMaterialService, VariantService, DesignService, CollectionService

from .services_size_series import SizeSeriesService, SizeService

from .services import ColorService, LineService, SublineService, TargetService

from .schemas import line_fields, subline_fields, color_fields, size_series_fields, size_fields
from .schemas import product_fields, product_design_fields, product_variant_material_detail_fields
from .schemas import product_variant_fields, collection_fields




#****************Products*****************************

class ProductGetResource(BaseGetResource):
    schema_get = staticmethod(ProductService.get_obj)
    schema_list = staticmethod( lambda: ProductService.get_obj_list(request.args.to_dict()))
    output_fields = product_fields


class ProductPostResource(BasePostResource):
    service_create = staticmethod(ProductService.create_obj)
    output_fields = product_fields
    file_fields = {
        'images': 'products'
    }


class ProductPatchResource(BasePatchResource):
    service_get = staticmethod(ProductService.get_obj)
    service_patch = staticmethod(ProductService.patch_obj)
    output_fields = product_fields


class ProductDeleteResource(BaseDeleteResource):
    service_get = staticmethod(ProductService.get_obj)
    service_delete = staticmethod(ProductService.delete_obj)



class NextProductCodeGetResource(Resource):
    def get(self):
        line_id = request.args.get('line_id', type=int)
        subline_id = request.args.get('subline_id', type=int)
        target_id = request.args.get('target_id', type=int)
        collection_id = request.args.get('collection_id', type=int)
        
        code = ProductService.preview_new_code(line_id=line_id, target_id=target_id, collection_id=collection_id, subline_id=subline_id)
        return success_response(str(code), 200)
        
        
#**************************ProductDesign***********************************
#************************************************************************
class ProductDesignGetResource(BaseGetResource):
    schema_get = staticmethod(DesignService.get_obj)
    schema_list = staticmethod( lambda: DesignService.get_obj_list(request.args.to_dict()))
    output_fields = product_design_fields


class ProductDesignPostResource(BasePostResource):
    service_create = staticmethod(DesignService.create_obj)
    output_fields = product_design_fields
    file_fields    = {
        'images': 'designs'
    }



class ProductDesignPatchResource(BasePatchResource):
    service_get = staticmethod(DesignService.get_obj)
    service_patch = staticmethod(DesignService.patch_obj)
    output_fields = product_design_fields


class ProductDesignDeleteResource(BaseDeleteResource):
    service_get = staticmethod(DesignService.get_obj)
    service_delete = staticmethod(DesignService.delete_obj)


#**************************ProdcutVariant***********************************
#**************************************************************************
class ProductVariantGetResource(BaseGetResource):
    schema_get = staticmethod(VariantService.get_obj)
    schema_list = staticmethod(lambda: VariantService.get_obj_list(request.args.to_dict()))
    output_fields = product_variant_fields

class ProductVariantListResource(BaseGetResource):
    output_fields = product_variant_fields

    @staticmethod
    def schema_list():
        product_id = request.view_args.get("product_id")
        return VariantService.get_obj_list_by_product(product_id)

class ProductVariantPostResource(BasePostResource):
    service_create = staticmethod(VariantService.create_variants_obj)
    output_fields = product_variant_fields


class ProductVariantPatchResource(BasePatchResource):
    service_get = staticmethod(VariantService.get_obj)
    service_patch = staticmethod(VariantService.patch_obj)
    output_fields = product_variant_fields


class ProductVariantDeleteResource(BaseDeleteResource):
    service_delete = VariantService.delete_obj

        
#***************************** VariantMaterialDetail***************************

class ProductVariantMaterialListResource(BaseGetResource):
    output_fields = product_variant_material_detail_fields
    schema_get = staticmethod(ProductVariantMaterialService.get_obj)
    schema_list = staticmethod(lambda: ProductVariantMaterialService.get_obj_list(request.args.to_dict()))

class VariantMaterialsGetResource(BaseGetResource):
    output_fields = product_variant_material_detail_fields
    schema_get = staticmethod(ProductVariantMaterialService.get_obj_list_by_variant)

class ProductVariantMaterialPostResource(BasePostResource):
    service_create = staticmethod(ProductVariantMaterialService.create_obj)
    output_fields = product_variant_material_detail_fields


class ProductVariantMaterialPatchResource(BasePatchResource):
    service_get = staticmethod(ProductVariantMaterialService.get_obj)
    service_patch = staticmethod(ProductVariantMaterialService.patch_obj)
    output_fields = product_variant_material_detail_fields


class ProductVariantMaterialDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(ProductVariantMaterialService.delete_obj)


#***********************VariantImage*****************************************
#***************************************************************************
class ProductVariantImagePostResource(Resource):
    def post(self, variant_id):
        try:
            pass

        except Exception as e:
            return error_response(f"Error al subir imagen: {str(e)}", 500)

class ProductVariantImageGetResource(Resource):
    def get(self, variant_id):
        try:
            pass
        except Exception as e:
            return error_response(f"Error al obtener imágenes: {str(e)}")


class ProductVariantImageDeleteResource(Resource):
    def delete(self, image_id):
        try:
            pass
        except Exception as e:
            return error_response(f"Error al eliminar imagen: {str(e)}")


#/*************************************************************************************

        




#****************************Sizes*****************************************

class SizeGetResource(BaseGetResource):
    schema_get = staticmethod(SizeService.get_obj)
    schema_list = staticmethod( lambda: SizeService.get_obj_list(request.args.to_dict()))
    output_fields = size_fields

class SerieSizesGetReosurce(BaseGetResource):
    schema_get = staticmethod(SizeService.get_sizes_by_serie)
    output_fields = size_fields

class SizePostResource(BasePostResource):
    pass
    service_create = staticmethod(SizeService)
    output_fields = size_fields

"""
class SizePatchResource(BasePatchResource):
    schema_validate_partial = validate_size_update
    service_patch = staticmethod(SizeServices.update_size)
    output_fields = size_fields
"""

class SizeDeleteResource(BaseDeleteResource):
    pass


class SeriesGetResource(BaseGetResource):
    schema_get = staticmethod(SizeSeriesService.get_obj)
    schema_list = staticmethod(lambda: SizeSeriesService.get_obj_list(request.args.to_dict()))
    output_fields = size_series_fields


class SeriesPostResource(BasePostResource):
    service_create = staticmethod(SizeSeriesService.create_obj)
    output_fields = size_series_fields


class SeriesPatchResource(BasePatchResource):
    service_get = staticmethod(SizeSeriesService.get_obj)
    service_patch = staticmethod(SizeSeriesService.patch_obj)
    output_fields = size_series_fields


class SeriesDeleteResource(BaseDeleteResource):
    service_get = staticmethod(SizeSeriesService.get_obj)
    service_delete = staticmethod(SizeSeriesService.delete_obj)



#*********************Colors**************************************
#******************************************************************************
class ColorGetResource(BaseGetResource):
    schema_get = staticmethod(ColorService.get_obj)
    schema_list = staticmethod( lambda: ColorService.get_obj_list(request.args.to_dict()))
    output_fields = color_fields

class ColorPostResource(BasePostResource):
    from .validations import validate_color_input
    schema = staticmethod(validate_color_input)
    service_create = staticmethod(ColorService.create_obj)
    output_fields = color_fields

class ColorPatchResource(BasePatchResource):
    from .validations import validate_color_patch
    schema_validate_partial = staticmethod(validate_color_patch)
    service_get = staticmethod(ColorService.get_obj)
    service_patch = staticmethod(ColorService.patch_obj)
    output_fields = color_fields

class ColorDeleteResource(BaseDeleteResource):
    service_get = staticmethod(ColorService.get_obj)
    service_delete = staticmethod(ColorService.delete_obj)



#---------------------------------------------------------------
#---------------------------Line---------------------------------

class LineGetResource(BaseGetResource):
    schema_get = staticmethod(LineService.get_obj)
    schema_list = staticmethod( lambda: LineService.get_obj_list(request.args.to_dict()))
    output_fields = line_fields

class LinePostResource(BasePostResource):
    service_create = staticmethod(LineService.create_obj)
    output_fields = line_fields

class LinePatchResource(BasePatchResource):
    service_get = staticmethod(LineService.get_obj)
    service_patch = staticmethod(LineService.patch_obj)
    output_fields = line_fields

#---------------------------------------------------------------
#---------------------------SubLine---------------------------------

class SubLineGetResource(BaseGetResource):
    schema_get = staticmethod(SublineService.get_obj)
    schema_list = staticmethod( lambda: SublineService.get_obj_list(request.args.to_dict()))
    output_fields = subline_fields

class SubLinePostResource(BasePostResource):
    service_create = staticmethod(SublineService.create_obj)
    output_fields = subline_fields

class SubLinePatchResource(BasePatchResource):
    service_get = staticmethod(SublineService.get_obj)
    service_patch = staticmethod(SublineService.patch_obj)
    output_fields = subline_fields


#--------------------------------------------------------------
#------------------------------Target----------------------------
class TargetGetResource(BaseGetResource):
    schema_get = staticmethod(TargetService.get_obj)
    schema_list = staticmethod( lambda: TargetService.get_obj_list(request.args.to_dict()))
    output_fields = line_fields

#*----------------------------------------------------------------
#---------------------------Collection------------------------------

class CollectionGetResource(BaseGetResource):
    schema_get = staticmethod(CollectionService.get_obj)
    schema_list = staticmethod( lambda: CollectionService.get_obj_list(request.args.to_dict()))
    output_fields = collection_fields

class CollectionGetSpecificResource(BaseGetResource):
    schema_get = staticmethod(CollectionService.get_obj)
    schema_list = staticmethod( lambda: CollectionService.get_specific_list(request.args.to_dict()))
    output_fields = collection_fields

class CollectionPostResource(BasePostResource):
    service_create = staticmethod(CollectionService.create_obj)
    output_fields = line_fields

class CollectionPatchResource(BasePatchResource):
    service_get = staticmethod(CollectionService.get_obj)
    service_patch = staticmethod(CollectionService.patch_obj)
    output_fields = collection_fields

class NextCodeCollectionCodeResource(Resource):
    def get(self):
        line_id = request.args.get('line_id', type=int)
        subline_id = request.args.get('subline_id', type=int)
        target_id = request.args.get('target_id', type=int)


        number = CollectionService.preview_collection_code(line_id, subline_id, target_id)
        if number:
            return ({'preview_code': str(number)})
        