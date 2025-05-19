from app import db

from flask import current_app
from werkzeug.utils import secure_filename
from .models import Product, ProductLine, ProductSubLine, ProductVariant, ProductVariantMaterialDetail, ProductVariantImage
from .models import ProductVariantColor, Color, SizeSeries, Size
from ..core.exceptions import *

from ..core.filters import apply_filters
from ..core.utils import FileUploader

from .utils import generate_variant_code
import os

import pandas as pd

class ProductServices:

    @staticmethod
    def get_obj_list(filters=None):
        from .models import Product
        return apply_filters(Product, filters)
    
    @staticmethod
    def get_obj(product_id):
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundError('Recurso no encontrado')
        return product
    
    @staticmethod
    def create_obj(data:dict):
        if Product.query.filter_by(code=data["code"]).first():
            raise ConflictError("Ya existe un producto con este código.")

        product = ProductServices._create_product(data)
        variant_data = data.get("variant")

        if not variant_data:
            raise ValidationError("Debes incluir al menos una variante inicial.")

        variant = ProductVariantService._create_variant(product, variant_data)
        ProductVariantService._add_colors_to_variant(variant, variant_data["color_ids"])
        ProductVariantService._add_materials_to_variant(variant, variant_data)
        try:
            db.session.commit()
            return product
        except:
            db.session.rollback()
            current_app.logger.warning('Error creando el producto')
            raise

    # ----------------------- Sub-funciones privadas ------------------------

    @staticmethod
    def _create_product(data):
        product = Product(
            code=data["code"].strip().upper(),
            name=data["name"].strip(),
            line_id=data.get("line_id"),
            sub_line_id=data.get("sub_line_id"),
            description=data.get("description")
        )
        db.session.add(product)
        db.session.flush()
        return product

    
    @staticmethod
    def patch_obj(instance, data):
        if 'code' in data:
            instance.code = data['code'].strip().upper()
        if 'name' in data:
            instance.name = data['name'].strip()
        if 'description' in data:
            instance.description = data['description']
        if 'line_id' in data:
            instance.line_id = data['line_id']
        if 'sub_line_id' in data:
            instance.sub_line_id = data['sub_line_id']
        try:
            db.session.commit()
            return instance
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al acualizar. e:{str(e)}')
            raise
    
    
    def delete_obj(product_id):
        """
        Elimina un producto y sus imágenes asociadas.
        :param product_id: ID del producto.
        """
        pass


class ProductVariantService:

    @staticmethod
    def get_obj(variant_id):
        variant = ProductVariant.query.get(variant_id)
        if not variant:
            raise NotFoundError("Variante no encontrada.")
        return variant
    
    @staticmethod
    def get_obj_list(filters=None):
        
        return apply_filters(ProductVariant, filters)

    @staticmethod
    def get_obj_list_by_product(product_id):
        return ProductVariant.query.filter_by(product_id=product_id).all()

    @staticmethod
    def _check_foreign_keys(data):
        if not Product.query.get(data["product_id"]):
            raise ValidationError("Producto no válido.")
        if not Size.query.get(data["size_id"]):
            raise ValidationError("Talla no válida.")
        for cid in data["color_ids"]:
            if not Color.query.get(cid):
                raise ValidationError(f"Color inválido: {cid}")
            
    @staticmethod
    def create_obj(data):
        product = Product.query.get(str(data['product_id']))
        variant = ProductVariantService._create_variant(product, data)
        ProductVariantService._add_colors_to_variant(variant, data['color_ids'])
        ProductVariantService._add_materials_to_variant(variant, data)

        try:
            db.session.commit()
            return variant
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error creando variante: {e}')

    @staticmethod
    def _create_variant(product, variant_data):
        # Validaciones
        if not variant_data.get("size_id"):
            raise ValidationError("Debes indicar la talla de la variante.")

        color_ids = variant_data.get("color_ids", [])
        if not color_ids or not isinstance(color_ids, list):
            raise ValidationError("Debes proporcionar al menos un color.")

        # Verificar existencia de size
        size = Size.query.get(variant_data["size_id"])
        if not size:
            raise ValidationError("La talla especificada no existe.")

        # Verificar existencia de colores
        color_objs = Color.query.filter(Color.id.in_(color_ids)).all()
        if len(color_objs) != len(set(color_ids)):
            raise ValidationError("Alguno de los colores especificados no existe.")

        # Generar código único para la variante
        color_codes = [c.code for c in color_objs]
        variant_code = generate_variant_code(product.code, color_codes)

        # Crear la variante
        variant = ProductVariant(
            product_id=product.id,
            size_id=variant_data["size_id"],
            code=variant_code,
            barcode=variant_data.get("barcode"),
            stock=0
        )
        db.session.add(variant)
        db.session.flush()  # para obtener ID
        return variant
    

    @staticmethod
    def _add_materials_to_variant(variant, variant_data):
        materials = variant_data.get("materials", [])
        serie_id = variant_data.get("serie_id")

        for mat in materials:
            db.session.add(ProductVariantMaterialDetail(
                variant_id=variant.id,
                material_id=mat["material_id"],
                serie_id=serie_id,
                quantity=mat["quantity"]
            ))

    @staticmethod
    def _add_colors_to_variant(variant, color_ids):
        if not color_ids or not isinstance(color_ids, list):
            raise ValidationError("Debes proporcionar una lista de colores válida.")

        for cid in color_ids:
            if not Color.query.get(cid):
                raise ValidationError(f"Color no válido: {cid}")
            db.session.add(ProductVariantColor(
                variant_id=variant.id,
                color_id=cid
            ))

    @staticmethod
    def patch_obj(instance, data):
        if "barcode" in data:
            instance.barcode = data["barcode"]
        if "stock" in data:
            instance.stock = data["stock"]

        if "color_ids" in data:
            # Reemplazar los colores
            ProductVariantColor.query.filter_by(variant_id=instance.id).delete()
            for cid in data["color_ids"]:
                if not Color.query.get(cid):
                    raise ValidationError(f"Color inválido: {cid}")
                db.session.add(ProductVariantColor(variant_id=instance.id, color_id=cid))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

        return instance

    @staticmethod
    def delete_obj(variant_id):
        variant = ProductVariant.query.get(variant_id)
        if not variant:
            raise NotFoundError("Variante no encontrada.")

        db.session.delete(variant)
        db.session.commit()
        return True   


class ProductVariantMaterialService:

    @staticmethod
    def get_obj(variant_material_id):
        obj = ProductVariantMaterialDetail.query.get(variant_material_id)
        if not obj:
            raise NotFoundError("Material de variante no encontrado.")
        return obj

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductVariantMaterialDetail, filters)
    
    @staticmethod
    def get_obj_list_by_product(product_id):
        return ProductVariant.query.filter_by(product_id=product_id).all()
    
    @staticmethod
    def _check_foreign_keys(data):
        from ..materials.models import Material
        if not ProductVariant.query.get(data["variant_id"]):
            raise ValidationError("La variante no existe.")
        if not Material.query.get(data["material_id"]):
            raise ValidationError("El material no existe.")
        if not SizeSeries.query.get(data["serie_id"]):
            raise ValidationError("La serie de tallas no existe.")


    @staticmethod
    def create_obj(data):
               
        ProductVariantMaterialService._check_foreign_keys(data)
             
        obj = ProductVariantMaterialDetail(
            variant_id=data["variant_id"],
            material_id=data["material_id"],
            serie_id=data["serie_id"],
            quantity=data["quantity"]
        )
        db.session.add(obj)
        try:
            db.session.commit()
            return obj
        except:
            db.session.rollback()
            current_app.logger.warning('Error al crear la variante BOM')
            raise

    @staticmethod
    def patch_obj(instance, data):
        if "quantity" in data:
            instance.quantity = data["quantity"]
        if "serie_id" in data:
            instance.serie_id = data["serie_id"]
        if "material_id" in data:
            instance.material_id = data["material_id"]

        db.session.commit()
        return instance

    @staticmethod
    def delete_obj(id):
        obj = ProductVariantMaterialDetail.query.get(id)
        if not obj:
            raise NotFoundError("No existe este material asociado.")
        db.session.delete(obj)
        db.session.commit()
        return True

class ProductVariantImageService:

    @staticmethod
    def get_images_by_variant(variant_id):
        return ProductVariantImage.query.filter_by(variant_id=variant_id).all()
    
    @staticmethod
    def delete_image(image_id):
        image = ProductVariantImage.query.get(image_id)
        if not image:
            raise NotFoundError("Imagen no encontrada.")

        # Eliminar archivo físico (opcional)
        try:
            file_path = os.path.join(current_app.root_path, 'static', image.file_path.replace('/static/', ''))
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            current_app.logger.warning(f"No se pudo borrar archivo físico: {e}")

        db.session.delete(image)
        db.session.commit()
        return True

    @staticmethod
    def create_image(variant_id, file):
        # Verificar que la variante exista
        if not ProductVariant.query.get(variant_id):
            raise NotFoundError("La variante no existe.")

        # Subir imagen usando el servicio genérico
        try:
            public_path = FileUploader.save_file(
                file=file,
                subfolder='products',
                entity_id=variant_id
            )
        except ValueError as e:
            raise ValidationError(str(e))

        # Registrar en base de datos
        image = ProductVariantImage(
            variant_id=variant_id,
            file_name=file.filename,
            file_path=public_path
        )
        db.session.add(image)
        db.session.commit()
        return image


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
        
        new_subline = ProductSubLine(code=code,
                                name = name,
                                description = description)
        db.session.add(new_subline)
        try:
            db.session.commit()
            return new_subline
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error guardando sublinea: {e}')


class ColorServices:
    
    @staticmethod
    def get_obj_list(filters = None ):
        
        """
        query = Color.query
        if filters:
            if 'code' in filters:
                query = query.filter(Color.code == str(filters['code'].upper()))
            if 'hex_value' in filters:
                query = query.filter(Color.hex_value == str(filters['hex_value']))
            if 'name' in filters:
                query = query.filter(Color.name.ilike(f"%{filters['name']}%"))

        return query.all()
        """
        return apply_filters(Color,filters)
    
        
    @staticmethod
    def get_obj(color_id):
        color = Color.query.get(color_id)
        if not color:
            raise NotFoundError("Color no encontrado")
        return color
    
    @staticmethod
    def create_obj(data):
        if Color.query.filter_by(code=data['code']).first():
            raise ConflictError("Ya existe un color con ese código.")
        
        new_color = Color(code = data['code'],
                        name = data['name'],
                        hex_value = data.get('hex_value'),
                        description = data.get('description'))
        db.session.add(new_color)
        try:
            db.session.commit()
            current_app.logger.info(f'Nuevo color guardado. {new_color.name}')
            return new_color
        except:
            db.session.rollback()
            current_app.logger.warning('Error al crear el color')
            raise     
        
    
    @staticmethod
    def patch_obj(instance, data):
        if 'name' in data:
            instance.name = data['name'].strip()
        if 'code' in data:
            if Color.query.filter_by(code=data['code']).first():
                raise ConflictError("Ya existe un color con ese código.")
            instance.code = data['code']
        if 'hex_value' in data:
            instance.hex_value = data['hex_value']
        if 'description' in data:
            instance.description = data['description']

        try:
            db.session.commit()
            return instance
        except:
            db.session.rollback()
            current_app.logger.warning('Error al actualizar el recurso')
            raise
    
    @staticmethod
    def delete_obj(id):
        color = Color.query.get(id)
        if not color:
            raise NotFoundError("Color no encontrado.")
        db.session.delete(color)
        db.session.commit()
        return True


#**************************SIZE SERVICES*******************************************
class SizeServices:

    @staticmethod
    def get_all_sizes(filters=None):
        query = Size.query
        if filters:
            if 'serie' in filters:
                query = query.filter(Size.series_id == int(filters['serie']))
            if 'value' in filters:
                query = query.filter(Size.value == str(filters['value']))
        
        return query.all()
    
    @staticmethod
    def get_size(size_id):
        size = Size.query.get(size_id)
        if not size:
            raise NotFoundError('Plan de pago no encontrado')
        return size
    
    
    @staticmethod
    def generate_sizes_for_series(series_id, start_size, end_size, step=1):
        current = start_size
        while current <= end_size:
            db.session.add(Size(value=str(current), series_id=series_id))
            current += step


    @staticmethod
    def create_size(value, series_id):
        series = db.session.get(SizeSeries, series_id)
        if not series:
            raise ValueError("Serie de tallas no encontrada")

        size = Size(value=value, series_id=series_id)
        db.session.add(size)
        try:
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise
        return size
    

    @staticmethod
    def delete_size(resource_id):
        size = db.session.get(Size, resource_id)
        if not size:
            return False
        db.session.delete(size)
        db.session.commit()
        return True



###***********************************SERIES SERVICES****************************************
class SeriesServices:

    @staticmethod
    def get_all_series(filters=None):
        query = SizeSeries.query
        if not filters:
            return query.all()
        
        if 'name' in filters:
            query = query.filter(SizeSeries.name == str(filters['name']))
            
        return query.all()
    
    @staticmethod
    def get_serie(serie_id):
        serie = SizeSeries.query.get(serie_id)
        if not serie:
            raise NotFoundError('Serie no encontrada')
        return serie
        
    @staticmethod
    def get_all_sizes():
        sizes = Size.query.all()
        return sizes
    
    @staticmethod
    def create_series(name,  start_size:int, end_size:int, description=None,):
        if end_size < start_size:
            raise AppError("La talla final no puede ser menor que la inicial")
        
        series = SizeSeries(name=name, description=description, start_size=start_size, end_size=end_size)
        db.session.add(series)
        db.session.flush()  # Consigue el ID

        SizeServices.generate_sizes_for_series(series.id, start_size, end_size)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise
        return series
    
    @staticmethod
    def delete_series(resource_id):
        series = db.session.get(SizeSeries, resource_id)
        if not series:
            return NotFoundError('Recurso no encontrado')
        db.session.delete(series)
        db.session.commit()
        return True
 
    
        
    @staticmethod
    def update_serie(instance, data):
        from .models import Size 

        changed_range = False

        if 'name' in data:
            instance.name = data['name'].strip()
        if 'description' in data:
            instance.description = data['description']
        if 'start_size' in data:
            instance.start_size = data['start_size']
            changed_range = True
        if 'end_size' in data:
            instance.end_size = data['end_size']
            changed_range = True
        
        if changed_range:
            # 1. Borrar tallas anteriores
            Size.query.filter(Size.series_id == instance.id).delete()
            db.session.flush()  # importante para no dejar tallas fantasma

            # 2. Regenerar tallas
            SizeServices.generate_sizes_for_series(instance.id, instance.start_size, instance.end_size)

        try:
            db.session.commit()
            return instance
        except:
            db.session.rollback()
            current_app.logger.warning(f'Error al actualizar serie e')
            raise

        
                 




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
        pass
        
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
        pass

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
        pass
           

    @staticmethod
    def save_product_images_at_db(product_id, image_paths):
        """
        Guarda las rutas de las imágenes asociadas a un producto en la base de datos.
        :param product_id: ID del producto.
        image_paths: Lista de rutas de las imágenes.
        """
        pass
           


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
        pass
      
        

