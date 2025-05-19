from flask import current_app, jsonify, request

from flask_restful import marshal, Resource

from sqlalchemy.exc import SQLAlchemyError

from ..core.utils import success_response, error_response

from ..core.resources import BasePatchResource, BaseGetResource, BasePostResource, BaseDeleteResource

from .services import ProductServices, ProductVariantMaterialService

from .services import ProductVariantService, ProductVariantImageService

from .services import SizeServices, SeriesServices

from .services import ColorServices

from .schemas import line_fields, subline_fields, color_fields, size_series_fields, size_fields
from .schemas import product_fields, material_detail_fields, variant_fields, variant_material_fields
from .schemas import product_variant_fields, variant_image_fields

from .validations import validate_size_create, validate_size_update, validate_size_series_update
from .validations import *
from .validations import validate_product_variant_materials_input



#****************Products*****************************

class ProductGetResource(BaseGetResource):
    schema_get = staticmethod(ProductServices.get_obj)
    schema_list = staticmethod( lambda: ProductServices.get_obj_list(request.args.to_dict()))
    output_fields = product_fields


class ProductPostResource(BasePostResource):
    schema = staticmethod(validate_product_input)
    service_create = staticmethod(ProductServices.create_obj)
    output_fields = product_fields


class ProductPatchResource(BasePatchResource):
    service_get = staticmethod(ProductServices.get_obj)
    schema_validate_partial = staticmethod(validate_product_patch_data)
    service_patch = staticmethod(ProductServices.patch_obj)
    output_fields = product_fields


class ProductDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(ProductServices.delete_obj)


#**************************ProdcutVariant***********************************
#**************************************************************************
class ProductVariantGetResource(BaseGetResource):
    schema_get = staticmethod(ProductVariantService.get_obj)
    schema_list = staticmethod(lambda: ProductVariantService.get_obj_list(request.args.to_dict()))
    output_fields = product_variant_fields

class ProductVariantListResource(BaseGetResource):
    output_fields = product_variant_fields

    @staticmethod
    def schema_list():
        product_id = request.view_args.get("product_id")
        return ProductVariantService.get_obj_list_by_product(product_id)

class ProductVariantPostResource(BasePostResource):
    schema = staticmethod(validate_variant_input)
    service_create = staticmethod(ProductVariantService.create_obj)
    output_fields = product_variant_fields


class ProductVariantPatchResource(BasePatchResource):
    service_get = staticmethod(ProductVariantService.get_obj)
    service_patch = staticmethod(ProductVariantService.patch_obj)
    schema_validate_partial = staticmethod(validate_variant_patch)
    output_fields = product_variant_fields


class ProductVariantDeleteResource(BaseDeleteResource):
    service_delete = ProductVariantService.delete_obj

        
#***************************** VariantMaterialDetail***************************

class ProductVariantMaterialListResource(BaseGetResource):
    output_fields = variant_material_fields
    schema_get = staticmethod(ProductVariantMaterialService.get_obj)
    schema_list = staticmethod(lambda: ProductVariantMaterialService.get_obj_list(request.args.to_dict()))


class ProductVariantMaterialPostResource(BasePostResource):
    schema = staticmethod(validate_product_variant_materials_input)
    service_create = staticmethod(ProductVariantMaterialService.create_obj)
    output_fields = variant_material_fields


class ProductVariantMaterialPatchResource(BasePatchResource):
    service_get = staticmethod(ProductVariantMaterialService.get_obj)
    service_patch = staticmethod(ProductVariantMaterialService.patch_obj)
    output_fields = variant_material_fields


class ProductVariantMaterialDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(ProductVariantMaterialService.delete_obj)


#***********************VariantImage*****************************************
#***************************************************************************
class ProductVariantImagePostResource(Resource):
    def post(self, variant_id):
        try:
            if 'file' not in request.files:
                return error_response("No se recibió archivo con clave 'file'.", 400)

            file = request.files['file']
            image = ProductVariantImageService.create_image(variant_id, file)
            return success_response(marshal(image, variant_image_fields), 201)

        except Exception as e:
            return error_response(f"Error al subir imagen: {str(e)}", 500)

class ProductVariantImageGetResource(Resource):
    def get(self, variant_id):
        try:
            images = ProductVariantImageService.get_images_by_variant(variant_id)
            return success_response(marshal(images, variant_image_fields))
        except Exception as e:
            return error_response(f"Error al obtener imágenes: {str(e)}")


class ProductVariantImageDeleteResource(Resource):
    def delete(self, image_id):
        try:
            deleted = ProductVariantImageService.delete_image(image_id)
            if deleted:
                return success_response({"message": "Imagen eliminada correctamente."})
        except Exception as e:
            return error_response(f"Error al eliminar imagen: {str(e)}")


#/*************************************************************************************
class NextCodeModelResource():
    def get(self):
        line_code = request.args.get('line')
        subline_code = request.args.get('subline')
        color_codes = request.args.getlist('colors')

        next_code = ProductServices.get_next_code_model(line_code, subline_code, color_codes)

        return jsonify({'next_code': next_code})
    

class ProcessBoomFileResource():

    def post(self):
        try:
            print('try post')
            # Verificar si se envió un archivo
            if 'file' not in request.files:
                return {"error": "No file part in the request"}, 400
            
            file = request.files['file']
            
            # Validar si se ha cargado un archivo
            if file.filename == '':
                return {"error": "No file selected"}, 400

            # Procesar el archivo usando el servicio
            boom_materials = None
            
            #if errors:
                #return {"errors": errors}, 400
            
            # Enviar los datos de productos para su previsualización en el frontend
            return {"boom": boom_materials}, 200
        
        except Exception as e:
            print(f'error procesando archivo: {e}')
            return {"error": f"Error processing file: {str(e)}"}, 500
        

class ProductImagesResource():
    
    def get(self, id=None):
        try:
            print(f'inside resource. pID:{id}')
            paths = None
            
            return paths, 200 if paths else 404
           
        except Exception as e:
            print(str(e))
            return {"error": f"Error processing file: {str(e)}"}, 500



        

class ProductPriceResource():

    def get(self, product_id):
        try:
            current_cost = ProductServices.calculate_material_cost(product_id)
            current_price = ProductServices.calculate_product_price(product_id)
            return {'cost': current_cost, 'price': current_price}, 200
        except Exception as e:
            return {"error": f"Error server: {str(e)}"}, 500
        


#****************************Sizes*****************************************

class SizeGetResource(BaseGetResource):
    schema_get = staticmethod(SizeServices.get_size)
    schema_list = staticmethod( lambda: SizeServices.get_all_sizes(request.args.to_dict()))
    output_fields = size_fields


class SizePostResource(BasePostResource):
    schema = validate_size_create
    service_create = staticmethod(SizeServices.create_size)
    output_fields = size_fields

"""
class SizePatchResource(BasePatchResource):
    schema_validate_partial = validate_size_update
    service_patch = staticmethod(SizeServices.update_size)
    output_fields = size_fields
"""

class SizeDeleteResource(BaseDeleteResource):
    service_delete = SeriesServices.delete_series


class SeriesGetResource(BaseGetResource):
    schema_get = staticmethod(SeriesServices.get_serie)
    schema_list = staticmethod(lambda: SeriesServices.get_all_series(request.args.to_dict()))
    output_fields = size_series_fields


class SeriesPostResource(BasePostResource):
    schema = staticmethod(validate_size_series_create)
    service_create = staticmethod(SeriesServices.create_series)
    output_fields = size_series_fields


class SeriesPatchResource(BasePatchResource):
    schema_validate_partial = staticmethod(validate_size_series_update)
    service_get = staticmethod(SeriesServices.get_serie)
    service_patch = staticmethod(SeriesServices.update_serie)
    output_fields = size_series_fields


class SeriesDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(SeriesServices.delete_series)



#*********************Colors**************************************
#******************************************************************************
class ColorGetResource(BaseGetResource):
    schema_get = staticmethod(ColorServices.get_obj)
    schema_list = staticmethod( lambda: ColorServices.get_obj_list(request.args.to_dict()))
    output_fields = color_fields

class ColorPostResource(BasePostResource):
    schema = staticmethod(validate_color_input)
    service_create = staticmethod(ColorServices.create_obj)
    output_fields = color_fields

class ColorPatchResource(BasePatchResource):
    schema_validate_partial = staticmethod(validate_color_patch)
    service_get = staticmethod(ColorServices.get_obj)
    service_patch = staticmethod(ColorServices.patch_obj)
    output_fields = color_fields

class ColorDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(ColorServices.delete_obj)