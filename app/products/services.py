from app import db

from flask import current_app

from .models import Product, ProductLine, ProductSubLine, Color, SizeSeries, Size, ProductMaterialDetail

import re

import pandas as pd

class ProductServices:

    @staticmethod
    def get_all_products():
        products = Product.query.all()
        return products
    
    @staticmethod
    def get_product(product_id):
        product = Product.query.get_or_404(product_id)
        return product
    
    @staticmethod
    def get_product_by_code(code):
        product = Product.query.filter_by(code=code).first()
        return product
    
    @staticmethod
    def create_product(line_id:int, code:str, color, subline_id=None, description=None, items=None):
        line = ProductLine.query.get_or_404(line_id)
        colorin = ColorServices.get_color(color)
        if subline_id:
            subline = ProductSubLine.query.get_or_404(subline_id)
            subline_id=subline.id
        else:
            subline_id=None
        if line:
            try:
                new_product = Product(code = code,
                                      color_id = color,
                                      name = 'namecitos',
                                      description = description,
                                      line_id = line_id,
                                      sub_line_id = subline_id)
                db.session.add(new_product)
                db.session.flush()
                BoomServices.create_boom_of_materials(new_product.id, items)
                db.session.commit()
                current_app.logger.info(f'Producto {new_product.name} creado')
            except Exception as e:
                db.session.rollback()
                current_app.logger.warning(f'Error creando producto: {str(e)}')
                raise ValueError(f'error al guardar modelo. e:{e}')

    @staticmethod
    def get_next_code_model(line, subline=None):
        from .models import Product
        subcode = str(line).upper()
        if subline:
            subcode += str(subline).upper()
        last_code = Product.query.filter(Product.code.startswith(subcode)).order_by(Product.code.asc()).first()
        if last_code is None:
            next_code = f"{subcode}001"
            return next_code
        
        # Extraer la parte numérica del último código encontrado
        last_code_number = re.search(r'\d+', last_code.code)
        if last_code_number:
            next_code_number = int(last_code_number.group()) + 1
            # Generar el siguiente código con ceros a la izquierda
            next_code = f"{subcode}{str(next_code_number).zfill(3)}"
        else:
            next_code = f"{subcode}001"  # En caso de no encontrar parte numérica

        return next_code
    

class ProductMaterialDetailServices:

    @staticmethod
    def get_product_material_detail(product_id):
        product_material_detail = ProductMaterialDetail.query.filter_by(product_id=product_id).all()
        return product_material_detail

class LineServices:

    @staticmethod
    def get_all_lines():
        lines = ProductLine.query.all()
        return lines
    
    @staticmethod
    def get_line(line_id):
        line = ProductLine.query.get_or_404(line_id)
        return line
    
    @staticmethod
    def create_line(code:str, name:str, description:str):
        try:
            new_line = ProductLine(code=code,
                                   name = name,
                                   description = description)
            db.session.add(new_line)
            db.session.commit()
            return new_line
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error guardando linea: {e}')
            raise Exception(e)
        

class SublineServices:

    @staticmethod
    def get_all_sublines():
        sublines = ProductSubLine.query.all()
        return sublines
    
    @staticmethod
    def get_subline(subline_id):
        subline = ProductSubLine.query.get_or_404(subline_id)
        return subline
    
    @staticmethod
    def create_subline(code:str, name:str, description:str=None):
        try:
            new_subline = ProductSubLine(code=code,
                                   name = name,
                                   description = description)
            db.session.add(new_subline)
            db.session.commit()
            return new_subline
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error guardando sublinea: {e}')


class ColorServices:
    
    @staticmethod
    def get_all_colors():
        colors = Color.query.all()
        return colors
        
    @staticmethod
    def get_color(color_id):
        color = Color.query.get_or_404(color_id)
        return color
    
    @staticmethod
    def get_color_by_code(color_code):
        color_code = str(color_code).upper()
        
        color = Color.query.filter_by(code = color_code).first()
        return color
    
    @staticmethod
    def create_color(code:str, name:str, hex:str=None, description:str=None):
        try:
            new_color = Color(code = code,
                            name = name,
                            hex_value = hex,
                            description = description)
            db.session.add(new_color)
            db.session.commit()
            current_app.logger.info(f'Nuevo color guardado. {new_color.name}')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al cuargar color e:{e}')


class SizeServices:

    @staticmethod
    def get_all_sizes():
        sizes = Size.query.all()
        return sizes
    
    @staticmethod
    def get_size(size_id):
        size = Size.query.get_or_404(size_id)
        return size
    
    @staticmethod
    def get_size_by_value(value):
        size = Size.query.filter_by(value=value).first()
        if size is None:
            return None
        return size


class SeriesServices:

    @staticmethod
    def get_all_series():
        series = SizeSeries.query.all()
        return series
    
    @staticmethod
    def get_serie(serie_id):
        serie = SizeSeries.query.get_or_404(serie_id)
        return serie

    @staticmethod
    def get_active_series():
        series = SizeSeries.query.filter(SizeSeries.is_active==True).all()
        return series
    
    @staticmethod
    def get_serie_by_size(size_value):
        try:
            size_obj = SizeServices.get_size_by_value(str(size_value))
            serie = size_obj.series.name
            return serie
        except Exception as e:
            current_app.logger.warning('No se puede obtener la serie')
            raise e


    @staticmethod
    def get_serie_by_code(query):
        print(query)
        if 'CODE=' in query:
            code = query.removeprefix('CODE=')         
        
        try:
            serie = SizeSeries.query.filter_by(name=code).first()
            
            return serie
        except Exception as e:
            raise ValueError(f'Ocurio un error e:{e}')
        
    
    @staticmethod
    def get_all_sizes():
        sizes = Size.query.all()
        return sizes
    
    @staticmethod
    def create_serie(name:str, start_size:int, end_size:int, description:str=None):
        if start_size<end_size:
            try:
                new_serie=SizeSeries(name = name,
                                    start_size= start_size,
                                    end_size = end_size,
                                    description = description)
                db.session.add(new_serie)
                db.session.flush() 
                
                sizes = [Size(value=str(size), series_id=new_serie.id) for size in range(start_size, end_size+1)]
               
                # Agregar todas las instancias de tamaño en una sola transacción
                db.session.add_all(sizes)
                
                db.session.commit()

                current_app.logger.info(f'Nueva serie creada')
            except Exception as e:
                db.session.rollback()
                current_app.logger.warning(f'Error al guardar serie e:{e}')
                raise ValueError('Ocurrio un error')
        else:
            raise ValueError('La talla de inicio debe ser menor a la talla final')
        
    @staticmethod
    def update_serie(serie_id:int, name:str, start_size:int, end_size:int, description:str=None):
        serie = SizeSeries.query.get_or_404(serie_id)
        
        serie.name = name,
        serie.start_size = start_size,
        serie.end_size = end_size,
        serie.description = description

        try:
            db.session.add(serie)
            db.session.commit()
            current_app.logger.info(f'Serie {serie.name} actualizda')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al actualizar serie e:{e}')


    @staticmethod 
    def delete_serie(serie_id):
        serie = SizeSeries.query.get_or_404(serie_id)
        try:
            db.session.delete(serie)
            db.session.commit()
            current_app.logger.info(f'Serie {serie.name} eliminada')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'No se pudo eliminar registro. <Serie {serie.name}>. Error: {e}')




class BoomServices:

    def process_boom_file(file):
        try:
            
            if file:
                file_extension = file.filename.split('.')[-1]
            if file_extension == 'csv':
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file, engine='openpyxl')
            
            from ..common.utils import process_boom_data
            
            columns = ['serie_code', 'material_code', 'detail', 'qty','unit']
            boom_materials = process_boom_data(df, columns)
        

            return boom_materials

        except Exception as e:
            raise Exception(f"Failed to process Excel file: {str(e)}")


    def create_boom_of_materials(product_id, items):
        from .models import ProductMaterialDetail, Material, SizeSeries
        
        try:
            if items:
            
                boom = []
                for item in items:
                    
                    material = Material.query.filter_by(code=item['code']).first()
                    material_id = material.id
                    serie = SizeSeries.query.filter_by(name=item['serie']).first()
                    new_product_material = ProductMaterialDetail(product_id=product_id,
                                                                 material_id = material_id,
                                                                 serie_id = serie.id,
                                                                 unit = material.unit,
                                                                 quantity = item['qty']
                                                                 )
                    boom.append(new_product_material)
                
                db.session.add_all(boom)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al guardar boom:{e}')
            raise ValueError(f'Ocurrio un error e:{e}')
        

class ImageServices:
    @staticmethod
    def get_images_from_db(product_id=None):
        print(product_id)
        url = 'static/media/products/E001NE/z1.webp'
        print(url)
        return url