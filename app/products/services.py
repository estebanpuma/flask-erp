from app import db
from sqlalchemy.exc import IntegrityError
from flask import current_app
from .models import Product, ProductLine, ProductSubLine, ProductVariant, ProductVariantMaterialDetail, ProductVariantImage
from .models import Color, SizeSeries, Size, ProductDesign
from .entities import ProductEntity, ProductDesignEntity, ProductVariantEntity, PatchProductEntity, ProductVariantMaterialEntity
from .services_size_series import SizeSeriesService, SizeService
from ..core.exceptions import *

from ..core.filters import apply_filters
from ..core.utils import FileUploader

from .dto_lines import LineCreateDTO, SublineCreateDTO, LineUpdateDTO, SublineUpdateDTO
import os

import pandas as pd

class ProductService:

    @staticmethod
    def create_obj(data:dict):
        try:
            with db.session.begin():
                product = ProductService.create_product(data)
                return product
        except Exception as e:
            current_app.logger.warning(f'Error al crear el producto. e:{e}')    
            raise e
        except IntegrityError:
            current_app.logger.warning('Error de inegridad')
            raise ConflictError('Error de duplicados')

    @staticmethod
    def create_product(data: dict) -> Product:
        """Crea un nuevo producto (opcionalmente con diseños)."""
        product = ProductEntity(data).to_model()
        from ..common.services import AppSettingService
        code = AppSettingService.get_next_product_code(product.code)
        product.code = code
        db.session.add(product)
        db.session.flush()  # Para obtener el ID

        # Si se proporcionan diseños, los crea
        designs_data = data.get("designs", [])
        if designs_data:
            DesignService.bulk_create_designs(product.id, designs_data)

        return product

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
    def patch_obj(instance:Product, data:dict):
        """Actualiza el producto"""

        if 'line_id' in data:
            line = LineService.get_line(data['line_id'])
            if line is None:
                raise ValidationError('No existe liena con esa id')
        if 'sub_line_id' in data:
            subline = SublineService.get_subline(data['sub_line_id'])
            if subline is None:
                raise ValidationError('N exise sublina con esa id')

        updated_product = PatchProductEntity(data).apply_changes(instance)
        try:
            db.session.commit()
            return updated_product
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning('No se puedo actualizar el producto')
            raise
    
    @staticmethod
    def delete_obj(instance):
        if not instance:
            raise NotFoundError('No se encontro el producto para borrar')
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al borrar producto')
            raise

class DesignService:

    @staticmethod
    def get_obj(id):
        design = ProductDesign.query.get(id)
        if not design:
            raise NotFoundError('No se encontro el diseno')
        return design
    
    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductDesign, filters)
    
    @staticmethod
    def patch_obj(instance:ProductDesign, data:dict)->ProductDesign:
        EDITABLE_FIELDS = {'description', 'name'}
        invalid_fields = set(data.keys()) - EDITABLE_FIELDS
        if invalid_fields:
            raise ValidationError(f"Campos no editables: {invalid_fields}")
        if 'description' in data:
            instance.description = str(data['description'])
        if 'name' in data:
            instance.name = str(data['name'])
        try:   
            db.session.commit()
            return instance
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning('Error al actualizar')
        
            
        
    @staticmethod
    def delete_obj(instance:ProductDesign):
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning('Error al borrar el diseno')
            raise

    @staticmethod
    def create_obj(data):
        """Crea un diseño con sus variantes y materiales."""
        try:
            with db.session.begin():
                design = DesignService.create_design(data)
                return design
        except Exception as e:
            current_app.logger.warning(f'Error al crear el diseno e:{e}')
            raise str(e)
        
    @staticmethod
    def create_design(data:dict) -> ProductDesign:
        """Funcion para crear un diseño con sus variantes y materiales."""

        product = Product.query.get(data['product_id'])
        if not product:
            raise ValidationError(f'No existe el producto con id: {str(data['product_id'])}')
        
        color_ids = data['color_ids']
        colors = []
        for color_id in color_ids:
            color = Color.query.get(color_id)
            if not color:
                raise ValidationError(f'No existe el color con id: {str(color_id)}')
            colors.append(color)


        # Genera el diseño
        design = ProductDesignEntity({
            "product_id": product.id,
            "color_ids": color_ids,
            "product_code": product.code,
            "color_codes": [c.code for c in colors],
            "series_ids": data['series_ids']
        }).to_model()

        db.session.add(design)
        print(f'hasta aqui los designs: {design}')
        design.colors.extend(colors)
        db.session.flush()
        
        # Crea variantes para cada serie/talla
        VariantService.bulk_create_variants(
            design_id=design.id,
            design_code=design.code,
            series_ids=data['series_ids'],
            materials=data['materials'],
        )
     
        return design

    @staticmethod
    def bulk_create_designs(product_id: int, designs_data: list) -> list[ProductDesign]:
        """
        Crea múltiples diseños en una SOLA transacción.
        - Usa add_all() para inserción masiva.
        """
        product = Product.query.get(product_id)
        if not product:
            raise ValidationError(f"Producto {product_id} no existe (at bulk)")

        designs = []
        designs_and_materials = []
  
        for design_data in designs_data:
            # Validar colores
            color_ids = design_data["color_ids"]
            colors = Color.query.filter(Color.id.in_(color_ids)).all()
            if len(colors) != len(color_ids):
                missing = set(color_ids) - {c.id for c in colors}
                raise ValidationError(f"Colores no encontrados: {missing}")

            print(f'Colores en buldesing; {colors}')
            # Crear diseño (sin commit)
            design = ProductDesignEntity({
                "product_id": product_id,
                "color_ids": color_ids,
                "product_code": product.code,
                "color_codes": [c.code for c in colors],
                "series_ids": design_data["series_ids"]
            }).to_model()
            print(f'desig en bulk desig : {design}')
            design.colors.extend(colors)
            print(f'design.colors: {design.colors}')
            designs.append(design)

            designs_and_materials.append({'design':design, 'materials':design_data['materials'], "series_ids": design_data["series_ids"]})
        
        db.session.add_all(designs)

        # Flush para obtener IDs de diseños
        db.session.flush()

        # Crear variantes para TODOS los diseños
        for design in designs_and_materials:
            variants = VariantService.bulk_create_variants(
                design_id=design['design'].id,
                design_code=design['design'].code,
                series_ids=design["series_ids"],
                materials=design["materials"],
            )

        
        return designs

    
class VariantService:

    @staticmethod
    def create_obj(data):
        return str('No se puede crear variantes individuales por el momento')
    
    @staticmethod
    def create_variants_obj(data):
        
        try:
            with db.session.begin():
                variants = VariantService.add_new_series_to_design(design_id=data['design_id'], 
                                                            series_ids=data['series_ids'], 
                                                            materials=data['materials'] )
                return variants
        except Exception as e:
            current_app.logger.warning(f'Error al crear nuevas variantes. e{e}')
            raise e
                
        

    @staticmethod
    def bulk_create_variants(design_id: int, design_code: str, series_ids: list, materials: dict):
        """Crea todas las variantes para un diseño con sus materiales."""
        # Validación temprana de series (mejor performance)
        series = SizeSeries.query.filter(SizeSeries.id.in_(series_ids)).all()
        if len(series) != len(series_ids):
            missing_ids = set(series_ids) - {s.id for s in series}
            raise ValidationError(f'Series no encontradas: {missing_ids}')

        variants = []
        
        # Creación de todas las variantes primero
        for serie in series:
            serie_materials = materials.get(str(serie.id), [])  # Materiales específicos para esta serie
            
            for size in serie.sizes:
                variant = ProductVariantEntity({
                    "design_id": design_id,
                    "size_id": size.id,
                    "design_code": design_code,
                    "size_value": size.value,
                    "materials": serie_materials
                }).to_model()
                
                db.session.add(variant)
                variants.append(variant)
                
                # Asignar materiales específicos de la serie
                #no hago flush porque ya tengo la relacion SQLALchemy
                #no incluyo variant_id porque la relacion lo hace por mi
                for mat in serie_materials:
                    variant.materials.append(ProductVariantMaterialDetail(
                        material_id=mat["material_id"],
                        quantity=mat["quantity"],
                    ))

        return variants
           

    @staticmethod
    def add_new_series_to_design(design_id: int, series_ids: list, materials: list) -> list[ProductVariant]:
        """Añade nuevas variantes a un diseño existente."""
        design = ProductDesign.query.get(design_id)
        if not design:
            raise ValidationError('No existe un diseno con el id indicado')
        return VariantService.bulk_create_variants(
            design_id=design.id,
            design_code=design.code,
            series_ids=series_ids,
            materials=materials,
        )

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
    def patch_obj(instance, data):
        if "barcode" in data:
            instance.barcode = data["barcode"]
        if "stock" in data:
            instance.stock = data["stock"]

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise
        except IntegrityError:
            db.session.rollback()
            current_app.logger.error("Error de integridad al crear variantes")
            raise

        return instance

    @staticmethod
    def delete_obj(instance):
        pass


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
    def get_obj_list_by_variant(variant_id):
        materials = ProductVariantMaterialDetail.query.filter(ProductVariantMaterialDetail.variant_id == variant_id).all()
        return materials
    
    @staticmethod
    def create_obj(data):
        with db.session.begin():
            created_materials = ProductVariantMaterialService.create_variant_material(data)
            return created_materials

    @staticmethod
    def create_variant_material(data):
        """
    Crea objetos ProductVariantMaterialDetail para un variant_id dado.
    No hace commit, solo añade a la sesión.
    """       
        ProductVariantMaterialService._check_foreign_keys(data)

        new_variant_materials = []

        for material in data['materials']:
            
            obj = ProductVariantMaterialEntity(
                {
                    'variant_id':data['variant_id'],
                    'material_id': material['material_id'],
                    'quantity': material['quantity']
                }
            ).to_model()
            new_variant_materials.append(obj)

        db.session.add_all(new_variant_materials)
        return new_variant_materials
        

    @staticmethod
    def patch_obj(instance, data:dict):
        EDITABLE_FIELDS = {'quantity'}
        invalid_fields = set(data.keys()) - EDITABLE_FIELDS
        if invalid_fields:
            raise ValidationError(f"Campos no editables: {invalid_fields}")
        
        if "quantity" in data:
            if data['quantity']>0:
                instance.quantity = data["quantity"]
            else:
                raise ValidationError('La cantidad debe ser mayor a 0')

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
    
    @staticmethod
    def _check_foreign_keys(data):
        from ..materials.models import Material
        if not ProductVariant.query.get(data["variant_id"]):
            raise ValidationError("La variante no existe.")
        

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


class LineService:

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductLine, filters)
    
    @staticmethod
    def get_obj(line_id):
        line = ProductLine.query.get(line_id)
        if not line:
            raise NotFoundError(f'No existe una linea con ID:{line_id}')
        return line
    
    @staticmethod
    def create_obj(data:dict)->ProductLine:
        with db.session.begin():
            dto = LineCreateDTO(**data)
            line = LineService.create_line(dto.code, dto.name, dto.description)
            return line
    
    @staticmethod
    def create_line(code:str, name:str, description:str):
        
        new_line = ProductLine(code=code,
                                name = name,
                                description = description)
        db.session.add(new_line)
        return new_line
    
    @staticmethod
    def patch_obj(obj:ProductLine, data:dict)->ProductLine:
        print('entra a patch obj')
        dto = LineUpdateDTO(**data)
        job = LineService.patch_line(obj, dto.name, dto.description)
        return job

    @staticmethod
    def patch_line(obj:ProductLine, name:str=None, description:str=None):
        print('entra a job')
        if name:
            if obj.name != name:
                obj.name = name
        if description:
            obj.description = description

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.warning(f'error: {e}')
            db.session.rollback()
            raise str(e)
    

        

class SublineService:

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductSubLine, filters)
    
    @staticmethod
    def get_obj(subline_id):
        subline = ProductSubLine.query.get(subline_id)
        if not subline:
            raise NotFoundError(f'No existe una sublinea con ID:{subline_id}')
        return subline
    
    @staticmethod
    def create_obj(data:dict)->ProductSubLine:
        with db.session.begin():
            dto = SublineCreateDTO(**data)
            subline = SublineService.create_subline(dto.code, dto.name, dto.description)
            return subline
    
    @staticmethod
    def create_subline(code:str, name:str, description:str):
        
        new_subline = ProductSubLine(code=code,
                                name = name,
                                description = description)
        db.session.add(new_subline)
        return new_subline
    
    @staticmethod
    def patch_obj(obj:ProductSubLine, data:dict)->ProductSubLine:
        print('entra a patch obj')
        dto = SublineUpdateDTO(**data)
        job = SublineService.patch_subline(obj, dto.name, dto.description)
        return job

    @staticmethod
    def patch_subline(obj:ProductSubLine, name:str=None, description:str=None):
        print('entra a job')
        if name:
            if obj.name != name:
                obj.name = name
        if description:
            obj.description = description

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.warning(f'error: {e}')
            db.session.rollback()
            raise str(e)


class ColorService:
    
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
class SizeService:

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
    def get_sizes_from_serie(serie_id):
        sizes = Size.query.filter(Size.series_id == serie_id).all()
        return sizes
    
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



        
                
        

