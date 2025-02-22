from app import db

from flask import current_app
from werkzeug.utils import secure_filename
from .models import Product, ProductLine, ProductSubLine, Color, SizeSeries, Size, ProductMaterialDetail, ProductImages
from .models import ProductColor, MaterialPriceHistory
import os

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
    def calculate_product_price(product_id):
        # Precio = Costo materiales + Costo mano de obra directa    
        try:
            material_cost = ProductServices.calculate_material_cost(product_id)['material_cost']
            print('material cost: ', material_cost)
            from ..pricing.services import PricingServices
            gross_margin = PricingServices.get_active_gross_margin()
            mcp = material_cost / (1 - (gross_margin.value)/100)
            return {'pvp': mcp}
        except Exception as e:
            current_app.logger.warning(f'Error calculando precio del producto: {str(e)}')
            return {'pvp': 0.0}
    
    @staticmethod
    def calculate_material_cost(product_id):
        try:
            product = ProductServices.get_product(product_id)
            # Costo materiales = sum( cantidad * precio_vigente )
            materials = product.material_details
            print('materials: ', materials)
            total_cost=0
            for material in materials:
                if material.material.current_price:
                    total_cost = material.material.current_price * material.quantity + total_cost
                print('totalcost', total_cost)

            material_cost = total_cost

            print('material cost: ', material_cost)
            return {
                "material_cost": material_cost,
                }
        except Exception as e:
            current_app.logger.warning(f'Error calculando costo de materiales: {str(e)}')
            return {
                "material_cost": 0.0,
            }

    @staticmethod
    def create_product(line_id:int, code:str, colors, name=None, subline_id=None, description=None, items=None, images=None):
        line = ProductLine.query.get_or_404(line_id)
       
        if subline_id:
            subline = ProductSubLine.query.get_or_404(subline_id)
            subline_id=subline.id
        else:
            subline_id=None
        if line:
            try:
                new_product = Product(code = code,
                                      name = name,
                                      description = description,
                                      line_id = line_id,
                                      sub_line_id = subline_id)
                db.session.add(new_product)
                db.session.flush()
                # Check if there are any valid images in the list
                valid_images = [image for image in images if image.filename != '']
                if valid_images:   
                    ImageServices.upload_and_save_images(valid_images, new_product.code, new_product.id)
                BoomServices.create_boom_of_materials(new_product.id, items)
                ColorServices.save_colors(new_product.id, colors)
                db.session.commit()
                current_app.logger.info(f'Producto {new_product.name} creado')
            except Exception as e:
                db.session.rollback()
                current_app.logger.warning(f'Error creando producto: {str(e)}')
                raise ValueError(f'error al guardar modelo. e:{e}')

    @staticmethod
    def get_next_code_model(line_code, subline_code=None, color_codes=None):
        # Get the line and subline IDs based on the provided codes
        line = ProductLine.query.filter_by(code=line_code).first()
        subline = ProductSubLine.query.filter_by(code=subline_code).first() if subline_code else None
        
        existing_codes = Product.query.filter(
            Product.line_id == line.id,
            (Product.sub_line_id == subline.id) if subline else (Product.sub_line_id == None),
            ).all()
        
        # Extract the sequence numbers from existing codes
        sequence_numbers = []
        for product in existing_codes:
            code = product.code
            # Extract the sequence number part of the code
            sequence_part = code[len(line_code) + (len(subline_code) if subline_code else 0):len(line_code) + (len(subline_code) if subline_code else 0) + 3]
            try:
                sequence_numbers.append(int(sequence_part))
            except ValueError:
                continue
        
        # Find the next sequence number
        next_sequence_number = max(sequence_numbers, default=0) + 1
        next_sequence_number_str = str(next_sequence_number).zfill(3)  # Ensure it's 3 digits

        # Construct the next code
        next_code = f"{line_code}{subline_code or ''}{next_sequence_number_str}{''.join(color_codes if color_codes else [])}"
        
        print('next code: ', next_code)
        return next_code
    

    def update_product(product_id,
                        line_id, 
                        code, colors, 
                        subline_id=None,
                        name=None,
                        description=None, 
                        items=None, 
                        images=None, 
                        existing_images=None):
        
        product = Product.query.get_or_404(product_id)
        line = ProductLine.query.get_or_404(line_id)
        if subline_id:
            subline = ProductSubLine.query.get_or_404(subline_id)
            subline_id=subline.id
        else:
            subline_id=None
        if line:
            try:
                product.code = code
                product.line_id = line_id
                product.sub_line_id = subline_id
                product.description = description
                db.session.add(product)
                db.session.flush()

                # Handle existing images
                if existing_images:
                    existing_image_paths = [image['url'].replace('/', '', 1) for image in existing_images]
                    current_images = ImageServices.get_images_from_db(product_id)
                    images_to_delete = set(current_images) - set(existing_image_paths)
                    for image_path in images_to_delete:
                        ImageServices.delete_uploaded_image(image_path)
                #handle new images
                # Check if there are any valid images in the list
                valid_images = [image for image in images if image.filename != '']
                print('valid images ', valid_images)
                if valid_images:   
                    ImageServices.upload_and_save_images(valid_images, product.code, product.id)
                BoomServices.create_boom_of_materials(product.id, items)
                ColorServices.update_colors(product.id, colors)
                db.session.commit()
                current_app.logger.info(f'Producto {product.name} actualizado')
            except Exception as e:
                db.session.rollback()
                current_app.logger.warning(f'Error actualizando producto: {str(e)}')
                raise ValueError(f'error al guardar modelo. e:{e}')
    
    def delete_product(product_id):
        """
        Elimina un producto y sus imágenes asociadas.
        :param product_id: ID del producto.
        """
        try:
            product = ProductServices.get_product(product_id)
            if product:
                # Delete associated images 
                
                ImageServices.delete_product_images(product_id)
                
                # Delete the product and associated images from the database
                db.session.delete(product)
                db.session.commit()
                current_app.logger.info(f'Producto {product.code} eliminado')
            else:
                raise ValueError('Producto no existe')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error eliminando el producto. e:{e}')
            raise

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
       
        
   
    @staticmethod
    def save_colors(product_id, colors_ids):
        """
        Saves a product color to the database.

        Args:
            product_id (int): The ID of the product.
            color_id (int): The ID of the color.

        Raises:
            ValueError: If there is an error while saving the product color.

        This function attempts to create a new ProductColor instance with the given
        product_id and color_id, adds it to the database session, and commits the session.
        If an exception occurs during this process, the session is rolled back, a warning
        is logged, and a ValueError is raised with the error message.
        """
        try:
            from .models import ProductColor
            for color in colors_ids:
                new_color = ProductColor(product_id=product_id, color_id=color['color'])
                db.session.add(new_color)
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error saving colors: {str(e)}')

            raise
    
    def update_colors(product_id, colors_ids):
        """
        Updates the colors associated with a product.

        Args:
            product_id (int): The ID of the product.
            colors_ids (list): List of color IDs.

        Raises:
            ValueError: If there is an error while updating the product colors.

        This function first deletes all existing ProductColor instances associated with the
        product, then creates new instances with the provided color IDs. If an exception occurs
        during this process, the session is rolled back, a warning is logged, and a ValueError is
        raised with the error message.
        """
        from .models import ProductColor
        try:
            # Delete existing product colors
            existing_colors = ProductColor.query.filter_by(product_id=product_id).all()
            for color in existing_colors:
                db.session.delete(color)
            
            # Save new colors
            for color in colors_ids:
                new_color = ProductColor(product_id=product_id, color_id=color['color'])
                db.session.add(new_color)

        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error updating product colors: {str(e)}')
            raise ValueError(f'Error updating product colors: {str(e)}')

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
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al guardar boom:{e}')
            raise ValueError(f'Ocurrio un error e:{e}')
        

class ImageServices:
    """
    Service class for handling image-related operations.
    """
    @staticmethod
    def get_images_from_db(product_id):
        """
        Obtiene las rutas de las imágenes asociadas a un producto.
        :param product_id: ID del producto.
        :return: Lista de rutas de las imágenes.
        """
        try:
            product = ProductServices.get_product(product_id)   
            images = product.images
            paths = [image.image_path for image in images]
            return paths
        except Exception as e:
            current_app.logger.warning(f"Error obteniendo imagees: {str(e)}")
            return []
        
    @staticmethod
    def allowed_file(filename):
        """
        Revisa si un archivo tiene una extensión permitida.
        :param filename: Nombre del archivo.
        :return: True si la extensión es permitida, False en caso contrario.
        """
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

    
    @staticmethod
    def save_image_at_server(image, product_code):
        """
        Guarda una imagen en el servidor y retorna su ruta relativa.
        :param image: Archivo subido (werkzeug.datastructures.FileStorage).
        :param product_code: Código único del producto.
        """
        if ImageServices.allowed_file(image.filename):
            try:
                filename = secure_filename(image.filename)
                relative_path = os.path.join('static','media','products', product_code, filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDERS']['products'], product_code, filename)
                dir_path = os.path.join(current_app.config['UPLOAD_FOLDERS']['products'], product_code)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                    print('path created')
                image.save(file_path)
                print('rp: ', relative_path)
                return relative_path
            except Exception as e:
                current_app.logger.warning(f'Error guardando imagen en el servidor: {e}')
                raise
        else:
            raise ValueError(f'Archivo {image.filename} No tiene una extension adecuada.')

    @staticmethod
    def upload_and_save_images(images, product_code, product_id):
        """
        Uploads images to the server and saves their relative paths.

        :param images: List of uploaded files (werkzeug.datastructures.FileStorage).
        :param product_code: Unique code of the product.
        :param product_id: ID of the product in the database.
        :return: List of relative paths of the saved files.
        :raises ValueError: If any file has an unsupported extension.
        """
        image_paths = []
        try:
            image_paths = [ImageServices.save_image_at_server(image, product_code) for image in images]
            ImageServices.save_product_images_at_db(product_id, image_paths)
            return image_paths
        except Exception as e:
            current_app.logger.warning(f'Error uploading images for product {product_id}: {e}')
           

    @staticmethod
    def save_product_images_at_db(product_id, image_paths):
        """
        Guarda las rutas de las imágenes asociadas a un producto en la base de datos.
        :param product_id: ID del producto.
        image_paths: Lista de rutas de las imágenes.
        """
        try:
            for path in image_paths:
                new_image = ProductImages(product_id=product_id, image_path=path)
                db.session.add(new_image)
            
        except Exception as e:  
            db.session.rollback()
            current_app.logger.warning(f'Error saving product images at db: {str(e)}')
            # Eliminar las imágenes subidas al servidor si ocurrió un error en la base de datos
            for path in image_paths:
                #full_path = os.path.join(current_app.config['UPLOAD_FOLDERS']['products'], path)
                if os.path.exists(path):
                    os.remove(path)
            raise ValueError(f'Error al guardar imagenes en la base de datos. e:{e}')
           


    @staticmethod
    def delete_uploaded_image(image_path):
        """
        Deletes an uploaded image from the server.

        :param image_path: The relative path of the image to be deleted.
        """
        try:
            full_path = os.path.join(current_app.config['UPLOAD_FOLDERS']['products'], image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                current_app.logger.info(f'Imagen eliminada: {full_path}')
            else:
                current_app.logger.warning(f'Imagen no encontrada: {full_path}')
        except Exception as e:
            current_app.logger.warning(f'Error eliminando la imagen: {e}')
            raise
        
    @staticmethod
    def delete_product_images(product_id):
        """
        Elimina las imágenes asociadas a un producto.
        :param product_id: ID del producto.
        :return: True si las imágenes fueron eliminadas exitosamente, False en caso contrario.
        """
        try:
            images = ProductImages.query.filter_by(product_id=product_id).all()
            for image in images:
                if ImageServices.delete_uploaded_image(image.image_path):
                    db.session.delete(image)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error eliminando imagenes: {str(e)}")
            return False
      
        

