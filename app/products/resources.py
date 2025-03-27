from flask import current_app, jsonify, request

from flask_restful import Resource, marshal, marshal_with, abort

from sqlalchemy.exc import SQLAlchemyError

from .services import ProductServices, SublineServices, LineServices,ColorServices, ProductMaterialDetailServices
from .services import ProductServices, SeriesServices, BoomServices, SizeServices, ImageServices

from .schemas import product_fields, line_fields, subline_fields, color_fields, size_series_fields, size_fields
from .schemas import product_material_detail_fields


class ProductResource(Resource):

    @marshal_with(product_fields)
    def get(self, product_id=None):
        try:
            qcode = request.args.get('code')

            if qcode:
                code = qcode.upper()
                product = ProductServices.get_product_by_code(code)
                return product, 200 if product else 404
            
            if product_id:
                product = ProductServices.get_product(product_id)
                return product, 200 if product else 404
            
            products = ProductServices.get_all_products()
            return products, 200
        
        except SQLAlchemyError as e:
            current_app.logger.warning(f'Error fetching models(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.warning(f'Unexpected error: {e}')
            abort(500, message="Unexpected error occurred")
        

class LineResource(Resource):
    
    @marshal_with(line_fields)
    def get(self, line_id=None):
        try:
            if line_id:
                line = LineServices.get_line(line_id)
                return line, 200
            lines = LineServices.get_all_lines()
            return lines,200
        
        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching line(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message="Unexpected error occurred")


class SubLineResource(Resource):
    
    @marshal_with(subline_fields)
    def get(self, subline_id=None):
        try:
            if subline_id:
                subline = SublineServices.get_subline(subline_id)
                return subline, 200
            sublines = SublineServices.get_all_sublines()
            return sublines,200
        
        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching subline(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message="Unexpected error occurred")


class ColorResource(Resource):
    
    @marshal_with(color_fields)
    def get(self, color_id=None):
        try:
            if color_id:
                color = ColorServices.get_color(color_id)
                return color, 200
            colors = ColorServices.get_all_colors()
            return colors,200
        
        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching color(s): {e}')
            abort(500, message=f"Internal server error: {e}")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message="Unexpected error occurred")


class SizeSeriesResource(Resource):

    @marshal_with(size_series_fields)
    def get(self, serie_id=None):

        query = request.args.get('q', '').upper()
        is_active = request.args.get('is_active')
        if is_active:
            print('entra a is activr')
            print(is_active)
            try:
                results = SeriesServices.get_active_series()
                return results, 200
            except Exception as e:
                current_app.logger.warning('Error al buscar Series activas')
                abort(500, message='Error')

        if query:
            try:
                results = SeriesServices.get_serie_by_code(query)
                
                return results, 200 
            except FileNotFoundError as e:
                return str(e), 404
            except Exception as e:
                return str(e), 500
        try:
            if serie_id:
                serie = SeriesServices.get_serie(serie_id)
                return serie, 200
            series = SeriesServices.get_all_series()
            return series, 200
        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching color(s): {e}')
            abort(500, message=f"Internal server error: {e}")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")


class SizeResource(Resource):

    @marshal_with(size_fields)
    def get(self, size_id=None):
        try:
            value = request.args.get('value')
            
            if value:
                size = SizeServices.get_size_by_value(value)
                if size is None:
                    abort(404, message='No encontrado')
                return size, 200

            if size_id:
                size = SizeServices.get_size(size_id)
                if size is None:
                    abort(404, message='No encontrado')
                return size, 200
            
            sizes = SizeServices.get_all_sizes()
            return sizes, 200
        
        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching color(s): {e}')
            abort(500, message=f"Internal server error: {e}")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message=f"Unexpected error occurred {e}")


class NextCodeModelResource(Resource):
    def get(self):
        line_code = request.args.get('line')
        subline_code = request.args.get('subline')
        color_codes = request.args.getlist('colors')

        next_code = ProductServices.get_next_code_model(line_code, subline_code, color_codes)

        return jsonify({'next_code': next_code})
    

class ProcessBoomFileResource(Resource):

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
            boom_materials = BoomServices.process_boom_file(file)
            
            #if errors:
                #return {"errors": errors}, 400
            
            # Enviar los datos de productos para su previsualización en el frontend
            return {"boom": boom_materials}, 200
        
        except Exception as e:
            print(f'error procesando archivo: {e}')
            return {"error": f"Error processing file: {str(e)}"}, 500
        

class ProductImagesResource(Resource):
    
    def get(self, id=None):
        try:
            print(f'inside resource. pID:{id}')
            paths = ImageServices.get_images_from_db(id)
            
            return paths, 200 if paths else 404
           
        except Exception as e:
            print(str(e))
            return {"error": f"Error processing file: {str(e)}"}, 500


class ProductMaterialDetailResource(Resource):

    @marshal_with(product_material_detail_fields)
    def get(self, product_id):
        try:
            product_material_detail = ProductMaterialDetailServices.get_product_material_detail(product_id)
            return product_material_detail, 200 if product_material_detail else 404
            
        except Exception as e:
            return {"error": f"Error processing file: {str(e)}"}, 500
        

class ProductPriceResource(Resource):

    def get(self, product_id):
        try:
            current_cost = ProductServices.calculate_material_cost(product_id)
            current_price = ProductServices.calculate_product_price(product_id)
            return {'cost': current_cost, 'price': current_price}, 200
        except Exception as e:
            return {"error": f"Error server: {str(e)}"}, 500