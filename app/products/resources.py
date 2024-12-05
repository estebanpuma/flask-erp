from flask import current_app, jsonify, request

from flask_restful import Resource, marshal, marshal_with, abort

from sqlalchemy.exc import SQLAlchemyError

from .services import ProductServices, SublineServices, LineServices,ColorServices, SeriesServices, BoomServices, SizeServices
from .schemas import product_fields, line_fields, subline_fields, color_fields, size_series_fields, size_fields


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
            current_app.logger.error(f'Error fetching users(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
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

    def get(self, line_code, subline_code=None):
        next_code = ProductServices.get_next_code_model(line_code, subline_code)

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