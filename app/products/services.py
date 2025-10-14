import json

from flask import current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from app import db

from ..common.services import ProductCodeGenerator
from ..core.exceptions import ConflictError, NotFoundError, ValidationError
from ..core.filters import apply_filters
from ..media.models import MediaFile
from .dto_lines import (
    CollectionCreateDTO,
    CollectionUpdateDTO,
    LineCreateDTO,
    LineUpdateDTO,
    SublineCreateDTO,
    SublineUpdateDTO,
)
from .dto_products import ProductCreateDTO, ProductDesignCreateDTO
from .models import (
    Color,
    Last,
    LastType,
    Product,
    ProductCollection,
    ProductDesign,
    ProductDesignImage,
    ProductLine,
    ProductSubLine,
    ProductTarget,
    ProductVariant,
    ProductVariantMaterialDetail,
    Size,
    SizeSeries,
)


class ProductService:

    @staticmethod
    def create_obj(data: dict):
        """Crea un nuevo producto."""
        with db.session.begin():
            # Determinar si el payload viene como un string JSON (de multipart) o ya es un dict (de application/json)
            if "data" in data:
                # Si 'data' existe, es probable que sea un string JSON de un FormData
                payload_source = data["data"]
            else:
                # Si no, los datos son el payload completo
                payload_source = data

            # Si la fuente es un string, la parseamos. Si ya es un dict, la usamos directamente.
            payload = (
                json.loads(payload_source)
                if isinstance(payload_source, str)
                else payload_source
            )

            dto = ProductCreateDTO.model_validate(payload)
            product = ProductService.create_product(
                target_id=dto.target_id,
                collection_id=dto.collection_id,
                name=dto.name,
                description=dto.description,
                line_id=dto.line_id,
                subline_id=dto.subline_id,
                designs=dto.colors,
                media_ids=dto.media_ids,
                old_code=dto.old_code,
                code=dto.code,
            )
            return product

    @staticmethod
    def create_product(
        name: str,
        designs: list,
        line_id: int,
        target_id: int,
        collection_id: int,
        code: str,
        media_ids: list[int] = None,
        old_code: str = None,
        subline_id: int = None,
        description: str = None,
    ) -> Product:
        """Crea un nuevo producto (opcionalmente con un diseño)."""

        # validaciones
        line = LineService.get_obj(line_id)
        if line is None:
            raise ValueError("Linea no encontrada")
        subline = None
        if subline_id is not None:
            subline = SublineService.get_obj(subline_id)
            if subline is None:
                raise ValueError("Sublinea no encontrada")
        target = TargetService.get_obj(target_id)
        if target is None:
            raise ValueError("Target no encontrada")
        collection = CollectionService.get_obj(collection_id)
        if collection is None:
            raise ValueError("Coleccion no encontrada")

        # code = ProductCodeGenerator.get_next_model_code(
        # linea=line, sublinea=subline, tipo=target, coleccion=collection
        # )

        product = Product(
            code=code,
            old_code=old_code,
            name=name,
            line_id=line_id,
            subline_id=subline_id,
            target_id=target_id,
            collection_id=collection_id,
            description=description,
            lifecycle_status="DRAFT",
        )
        db.session.add(product)
        db.session.flush()  # Para obtener el ID

        DesignService.create_design(
            product_id=product.id,
            color_ids=designs,
            name=name,
            description=description,
            media_ids=media_ids,
        )

        return product

    @staticmethod
    def get_obj_list(filters=None):
        from .models import Product

        return apply_filters(Product, filters)

    @staticmethod
    def get_obj(product_id):
        product = (
            db.session.query(Product)
            .options(joinedload(Product.designs))
            .get(product_id)
        )
        if not product:
            raise NotFoundError("Recurso no encontrado")
        return product

    @staticmethod
    def patch_obj(instance: Product, data: dict):
        """Actualiza el producto"""
        from .dto_products import ProductPatchDTO

        dto = ProductPatchDTO.model_validate(data)

        if dto.lifecycle_status is not None:
            UpdateLifecycleStatusService.update_status(instance, dto.lifecycle_status)

        if dto.name is not None:
            instance.name = dto.name
        if dto.description is not None:
            instance.description = dto.description
        if dto.old_code is not None:
            instance.old_code = dto.old_code
        db.session.add(instance)
        try:
            db.session.commit()
            print("instance pathec status: ", instance.lifecycle_status)
            return instance
        except Exception:
            db.session.rollback()
            current_app.logger.warning("No se puedo actualizar el producto")
            raise

    @staticmethod
    def delete_obj(instance):
        if not instance:
            raise NotFoundError("No se encontro el producto para borrar")
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            current_app.logger.warning("Error al borrar producto")
            raise

    @staticmethod
    def preview_new_code(
        line_id: int, target_id: int, collection_id: int, subline_id: int = None
    ):

        # validaciones
        line = LineService.get_obj(line_id)
        subline = None
        if subline_id is not None:
            subline = SublineService.get_obj(subline_id)
        target = TargetService.get_obj(target_id)
        collection = CollectionService.get_obj(collection_id)

        code = ProductCodeGenerator.preview_model_code(
            linea=line, sublinea=subline, tipo=target, coleccion=collection
        )
        return code


class DesignService:

    @staticmethod
    def get_obj(id):
        design = ProductDesign.query.get(id)
        if not design:
            raise NotFoundError("No se encontro el diseno")
        return design

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductDesign, filters)

    @staticmethod
    def patch_obj(instance: ProductDesign, data: dict) -> ProductDesign:
        from .dto_products import ProductDesignPatchDTO

        dto = ProductDesignPatchDTO.model_validate(data)
        if dto.name is not None:
            instance.name = dto.name
        if dto.lifecycle_status is not None:
            UpdateLifecycleStatusService.update_status(instance, dto.lifecycle_status)
        if dto.description is not None:
            instance.description = dto.description

        try:
            db.session.commit()
            return instance
        except Exception:
            db.session.rollback()
            current_app.logger.warning("Error al actualizar")

    @staticmethod
    def delete_obj(instance: ProductDesign):
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            current_app.logger.warning("Error al borrar el diseno")
            raise

    @staticmethod
    def create_obj(data: dict):
        """Crea un diseño simple"""

        with db.session.begin():
            dto = ProductDesignCreateDTO(data)
            design = DesignService.create_design(
                product_id=dto.product_id,
                color_ids=dto.color_ids,
                name=dto.name,
                description=dto.description,
            )
            return design

    @staticmethod
    def create_design(
        product_id: int,
        color_ids: list[int],
        name: str = None,
        media_ids: list[int] = None,
        description: str = None,
    ) -> ProductDesign:
        """Funcion para crear un diseño/color con sus variantes y materiales."""

        product: Product = Product.query.get(product_id)
        if not product:
            raise ValidationError(f"No existe el producto con id: {product_id}")
        colors: list[Color] = []
        color_ids = [c.id for c in color_ids]
        for color_id in color_ids:
            color = Color.query.get(color_id)
            if not color:
                raise ValidationError(f"No existe el color con id: {str(color_id)}")
            colors.append(color)
        colors_codes = [c.code.upper() for c in colors]
        color_part = "".join(colors_codes)
        c_code = f"{product.code}{str(color_part)}"
        old_code = f"{product.old_code}{str(color_part)}" if product.old_code else None
        # Genera el diseño
        design = ProductDesign(
            product_id=product_id,
            old_code=old_code,
            name=name,
            description=description,
            code=c_code,
            status="DRAFT",
        )
        db.session.add(design)
        design.colors.extend(colors)

        # Asociar imágenes si se proporcionaron IDs
        if media_ids:
            # Recuperamos los MediaFile dentro de la sesión actual
            media_files_to_associate = (
                db.session.query(MediaFile).filter(MediaFile.id.in_(media_ids)).all()
            )
            if len(media_files_to_associate) != len(media_ids):
                raise ValidationError("Uno o más IDs de imágenes no son válidos.")

            # Limpiamos asociaciones viejas (si las hubiera)
            design.image_associations.clear()
            for i, media_file in enumerate(media_files_to_associate):
                # Creamos una instancia del objeto de asociación
                association = ProductDesignImage(
                    media_file=media_file,
                    is_primary=(i == 0),  # La primera imagen es la primaria por defecto
                    order=i,
                )
                design.image_associations.append(association)

        return design

    @staticmethod
    def delete_image_from_design(design_id: int, image_id: int):
        """Elimina la asociación de una imagen con un diseño."""
        design = ProductDesign.query.get(design_id)
        if not design:
            raise NotFoundError("Diseño no encontrado.")

        association_to_delete = None
        for assoc in design.image_associations:
            if assoc.media_file_id == image_id:
                association_to_delete = assoc
                break

        if not association_to_delete:
            raise NotFoundError("La imagen no está asociada a este diseño.")

        # Elimina el objeto de la asociación
        db.session.delete(association_to_delete)
        db.session.commit()
        return True

    @staticmethod
    def bulk_create_designs(product_id: int, designs_data: list) -> list[ProductDesign]:
        """
        Crea uno o múltiples diseños en una SOLA transacción.
        - Usa add_all() para inserción masiva.
        """
        product = Product.query.get(product_id)
        if not product:
            raise ValidationError(f"Producto {product_id} no existe (at bulk)")

        designs = []

        for design_data in designs_data:
            # Validar colores
            color_ids = design_data.color_ids
            colors = Color.query.filter(Color.id.in_(color_ids)).all()
            if len(colors) != len(color_ids):
                missing = set(color_ids) - {c.id for c in colors}
                raise ValidationError(f"Colores no encontrados: {missing}")
            colors_codes = [c.code.upper() for c in colors]
            color_part = "".join(colors_codes)
            c_code = f"{product.code}{str(color_part)}"
            old_code = (
                f"{product.old_code}{str(color_part)}" if product.old_code else None
            )
            name = f"{product.name}-{color_part}" if product.name else None

            # Crear diseño (sin commit)
            design = ProductDesign(
                product_id=product_id,
                code=c_code,
                old_code=old_code,
                name=name,
            )
            design.colors.extend(colors)
            designs.append(design)

        db.session.add_all(designs)

        # Flush para obtener IDs de diseños
        db.session.flush()

        return designs


class VariantService:

    @staticmethod
    def create_obj(data: dict):
        from .dto_products import ProductVariantCreateDTO

        with db.session.begin():
            dto = ProductVariantCreateDTO.model_validate(data)
            print("dto: ", dto)
            variants = VariantService.create_variants(
                design_id=dto.design_id, sizes_ids=dto.sizes_ids
            )
            return variants

    @staticmethod
    def create_variants(design_id: int, sizes_ids: list[int]):
        """Crea variantes para un diseño a partir de una lista de IDs de tallas."""

        design: ProductDesign = ProductDesign.query.get(design_id)
        if design is None:
            raise ValidationError("Diseño no encontrado.")

        new_variants = []
        for size_id in sizes_ids:
            size: Size = Size.query.get(size_id)
            if size is None:
                raise ValidationError(f"Talla con id:{size_id} no encontrada.")
            new_variant = ProductVariant(
                design_id=design_id,
                size_id=size_id,
                code=f"{design.code}{size.value}",
                old_code=f"{design.old_code}{size.value}" if design.old_code else None,
            )
            new_variants.append(new_variant)
        db.session.add_all(new_variants)
        return new_variants

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
    def patch_obj(instance, data: dict):
        from .dto_products import ProductVariantPatchDTO

        dto = ProductVariantPatchDTO.model_validate(data)
        if dto.lifecycle_status is not None:
            UpdateLifecycleStatusService.update_status(instance, dto.lifecycle_status)
        try:
            db.session.commit()
            return instance
        except Exception:
            db.session.rollback()
            raise
        except IntegrityError:
            db.session.rollback()
            current_app.logger.error("Error de integridad al crear variantes")
            raise

    @staticmethod
    def delete_obj(instance):
        if not instance:
            raise NotFoundError("No se encontro la variante para borrar")
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            current_app.logger.warning("Error al borrar variante")
            raise


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
        materials = ProductVariantMaterialDetail.query.filter(
            ProductVariantMaterialDetail.variant_id == variant_id
        ).all()
        return materials

    @staticmethod
    def create_obj(data: dict):
        from .dto_products import VariantMaterialsCreateDTO

        with db.session.begin():
            dto = VariantMaterialsCreateDTO.model_validate(data)
            created_materials = ProductVariantMaterialService.create_variant_materials(
                variant_id=dto.variant_id, materials=dto.materials
            )
            return created_materials

    @staticmethod
    def create_variant_materials(variant_id: int, materials: list):
        """
        Crea objetos ProductVariantMaterialDetail para un variant_id dado.
        No hace commit, solo añade a la sesión.
        """
        variant = ProductVariant.query.get(variant_id)
        if variant is None:
            raise ValidationError("Variante no encontrada.")

        new_variant_materials = []

        for material in materials:

            obj = ProductVariantMaterialDetail(
                variant_id=variant_id,
                material_id=material.material_id,
                quantity=material.quantity,
            )
            new_variant_materials.append(obj)

        db.session.add_all(new_variant_materials)
        return new_variant_materials

    @staticmethod
    def patch_obj(instance: ProductVariantMaterialDetail, data: dict):
        from .dto_products import ProductVariantMaterialDetailPatchDTO

        dto = ProductVariantMaterialDetailPatchDTO.model_validate(data)
        if dto.quantity is None:
            raise ValueError("La cantidad no puede ser None.")
        instance.quantity = dto.quantity
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return instance

    @staticmethod
    def delete_obj(instance: ProductVariantMaterialDetail):
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def _check_foreign_keys(data):

        if not ProductVariant.query.get(data["variant_id"]):
            raise ValidationError("La variante no existe.")


class ProductDesignImageService:
    @staticmethod
    def create_obj(data: dict):
        from .dto_products import ProductDesignImageDTO

        with db.session.begin():
            dto = ProductDesignImageDTO(**data)
            new_images = ProductDesignImageService.add_images(
                media_ids=dto.media_ids,
                design_id=dto.design_id,
                is_primary=dto.is_primary,
                order=dto.order,
            )
            return new_images

        pass

    @staticmethod
    def add_images(
        media_ids: list[int], design_id: int, is_primary: bool = None, order: int = None
    ):
        from ..media.models import MediaFile

        design = ProductDesign.query.get(design_id)
        if design is None:
            raise ValidationError("Diseño no encontrado.")
        new_images = []
        for media_id in media_ids:
            media_file = MediaFile.query.get(media_id)
            if media_file is None:
                raise ValidationError(f"Imagen con id:{media_id} no encontrada.")

            new_image = ProductDesignImage(
                media_file=media_file,
                design=design,
                is_primary=is_primary,
                order=order,
            )
            new_images.append(new_image)
        db.session.add_all(new_images)
        return new_images

    @staticmethod
    def get_obj_list(id: int):
        query = db.session.query(ProductDesignImage).filter_by(design_id=id)
        return query.all()


class LineService:

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductLine, filters)

    @staticmethod
    def get_obj(line_id):
        line = ProductLine.query.get(line_id)
        if not line:
            raise NotFoundError(f"No existe una linea con ID:{line_id}")
        return line

    @staticmethod
    def create_obj(data: dict) -> ProductLine:
        with db.session.begin():
            dto = LineCreateDTO(**data)
            line = LineService.create_line(dto.code, dto.name, dto.description)
            return line

    @staticmethod
    def create_line(code: str, name: str, description: str):

        new_line = ProductLine(code=code.upper(), name=name, description=description)
        db.session.add(new_line)
        return new_line

    @staticmethod
    def patch_obj(obj: ProductLine, data: dict) -> ProductLine:
        print("entra a patch obj")
        dto = LineUpdateDTO(**data)
        obj = LineService.patch_line(obj, dto.name, dto.description, dto.is_active)
        return obj

    @staticmethod
    def patch_line(
        obj: ProductLine,
        name: str = None,
        description: str = None,
        is_active: bool = None,
    ):
        print("entra a job")
        if name:
            if obj.name != name:
                obj.name = name
        if description:
            obj.description = description

        if is_active is not None:
            # 1. Actualizar el objeto principal
            obj.is_active = is_active
            # 2. Actualizar colecciones: Filtramos por la relación (ForeignKey)
            db.session.query(ProductCollection).filter(
                ProductCollection.line_id == obj.id  # o el nombre de tu Foreign Key
            ).update(
                {ProductCollection.is_active: is_active}, synchronize_session="fetch"
            )

            # 3. Actualizar productos:
            db.session.query(Product).filter(
                Product.line_id == obj.id  # o el nombre de tu Foreign Key
            ).update({Product.is_active: is_active}, synchronize_session="fetch")

        try:
            db.session.commit()
            return obj
        except Exception as e:
            current_app.logger.warning(f"error: {e}")
            db.session.rollback()
            raise str(e)

    @staticmethod
    def delete_obj(obj: ProductLine):
        try:
            db.session.delete(obj)
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.warning(f"error: {e}")
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
            raise NotFoundError(f"No existe una sublinea con ID:{subline_id}")
        return subline

    @staticmethod
    def create_obj(data: dict) -> ProductSubLine:
        with db.session.begin():
            dto = SublineCreateDTO(**data)
            subline = SublineService.create_subline(dto.code, dto.name, dto.description)
            return subline

    @staticmethod
    def create_subline(code: str, name: str, description: str):

        new_subline = ProductSubLine(
            code=code.upper(), name=name, description=description
        )
        db.session.add(new_subline)
        return new_subline

    @staticmethod
    def patch_obj(obj: ProductSubLine, data: dict) -> ProductSubLine:
        print("entra a patch obj")
        dto = SublineUpdateDTO(**data)
        obj = SublineService.patch_subline(
            obj, dto.name, dto.description, dto.is_active
        )
        return obj

    @staticmethod
    def patch_subline(
        obj: ProductSubLine,
        name: str = None,
        description: str = None,
        is_active: bool = None,
    ):
        print("entra a job")
        if name:
            if obj.name != name:
                obj.name = name
        if description:
            obj.description = description

        if is_active is not None:
            obj.is_active = is_active
            db.session.query(ProductCollection).filter(
                ProductCollection.subline_id == obj.id
            ).update(
                {ProductCollection.is_active: is_active}, synchronize_session="fetch"
            )
            db.session.query(Product).filter(Product.subline_id == obj.id).update(
                {Product.is_active: is_active}, synchronize_session="fetch"
            )

        try:
            db.session.commit()
            return obj
        except Exception as e:
            current_app.logger.warning(f"error: {e}")
            db.session.rollback()
            raise str(e)

    @staticmethod
    def delete_obj(obj: ProductSubLine):
        try:
            db.session.delete(obj)
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.warning(f"error: {e}")
            db.session.rollback()
            raise str(e)


class TargetService:

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductTarget, filters)

    @staticmethod
    def get_obj(line_id):
        line = ProductTarget.query.get(line_id)
        if not line:
            raise NotFoundError(f"No existe una coleccion con ID:{line_id}")
        return line

    @staticmethod
    def create_obj(data: dict) -> ProductTarget:
        return "No implementado"
        # with db.session.begin():
        # dto = TargetCreateDTO(**data)
        # collection = CollectionService.create_target(dto.code, dto.name, dto.description)
        # return collection

    @staticmethod
    def create_target(code: str, name: str, description: str):

        new_target = ProductTarget(
            code=str(code).upper(), name=name, description=description
        )
        db.session.add(new_target)
        return new_target

    @staticmethod
    def patch_obj(obj: ProductTarget, data: dict) -> ProductTarget:
        return "Not implemented"

    @staticmethod
    def patch_target(obj: ProductTarget, name: str = None, description: str = None):
        print("entra a job")
        if name:
            if obj.name != name:
                obj.name = name
        if description:
            obj.description = description

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.warning(f"error: {e}")
            db.session.rollback()
            raise str(e)


class CollectionService:

    @staticmethod
    def get_obj_list(filters: dict = None):
        # 1. Base de la consulta con los eager-loads
        query = db.session.query(ProductCollection).options(
            joinedload(ProductCollection.line),
            joinedload(ProductCollection.sub_line),
            joinedload(ProductCollection.target),
        )

        # 2. Aplica cada filtro si existe y no es None
        if filters:
            # Por cada clave, usa filter() dinámicamente
            for field, value in filters.items():
                if value is None or value == "":
                    if field == "subline_id":
                        model_attr = getattr(ProductCollection, field, None)
                        query = query.filter(model_attr == value)
                    continue
                # Atributo en el modelo
                model_attr = getattr(ProductCollection, field, None)
                if model_attr is not None:
                    query = query.filter(model_attr == value)

        # 3. Ejecuta y devuelve
        return query.all()

    @staticmethod
    def get_specific_list(filters: dict = None):
        if "line_id" and "target_id" and "subline_id" in filters:
            query = (
                db.session.query(ProductCollection)
                .filter(
                    ProductCollection.line_id == filters["line_id"],
                    ProductCollection.subline_id == filters["subline_id"],
                    ProductCollection.target_id == filters["target_id"],
                )
                .all()
            )
            return query

        if "line_id" and "target_id" in filters:
            query = (
                db.session.query(ProductCollection)
                .filter(
                    ProductCollection.line_id == filters["line_id"],
                    ProductCollection.subline_id is None,
                    ProductCollection.target_id == filters["target_id"],
                )
                .all()
            )
            return query
        else:
            return "Proporcione datos"

    @staticmethod
    def get_obj(obj_id):

        obj = (
            db.session.query(ProductCollection)
            .options(
                joinedload(ProductCollection.line),  # Carga la relación "line"
                joinedload(ProductCollection.sub_line),  # Carga "sub_line"
                joinedload(ProductCollection.target),  # Carga "target"
            )
            .get(obj_id)
        )
        if not obj:
            raise NotFoundError(f"No existe una coleccion con ID:{obj_id}")
        return obj

    @staticmethod
    def create_obj(data: dict) -> ProductCollection:
        with db.session.begin():
            dto = CollectionCreateDTO(**data)
            collection = CollectionService.create_collection(
                line_id=dto.line,
                subline_id=dto.subline,
                target_id=dto.target,
                last_type_id=dto.last_type,
                code=dto.code,
                name=dto.name,
                description=dto.description,
            )
            return collection

    @staticmethod
    def preview_collection_code(line_id: int):
        from ..common.services import SecuenceGenerator

        line = LineService.get_obj(line_id)
        if line is None:
            raise ValueError("Linea no encontrada")

        code = SecuenceGenerator.get_next_number(f"collection_{line_id}")
        return code

    @staticmethod
    def create_collection(
        line_id: int,
        target_id: int,
        last_type_id: int,
        name: str,
        description: str,
        code: str,
        subline_id: int = None,
    ):
        from ..common.services import SecuenceGenerator

        line = LineService.get_obj(line_id)
        if line is None:
            raise ValueError("Linea no encontrada")

        subcode = line.code

        if subline_id:
            subline = SublineService.get_obj(subline_id)
            if subline is None:
                raise ValueError("Sublinea no encontrada")
            subcode = f"{line.code}{subline.code}"

        target = TargetService.get_obj(target_id)
        if target is None:
            raise ValueError("Target no encontrada")

        subcode = f"{subcode}{target.code}"

        if last_type_id:
            last_type = LastTypeService.get_obj(last_type_id)
            if last_type is None:
                raise ValueError("Horma no encontrada")

        if code:
            aux_code = f"{subcode}{str(code)}"
            # Validación de unicidad según restricción
            query = db.session.query(ProductCollection).filter_by(
                code=code, line_id=line_id, subline_id=subline_id, target_id=target_id
            )

            if query.first():
                raise ConflictError(
                    f"Ya existe una colección con código {code} para la combinación seleccionada."
                )
        else:
            sec = SecuenceGenerator.get_next_number(f"collection_{subcode}")
            code = sec
            aux_code = f"{subcode}{str(sec)}"

        existing = ProductCollection.query.filter(
            ProductCollection.aux_code == aux_code
        ).first()
        if existing:
            raise ConflictError(
                f"Ya existe una colección con código {aux_code} para la combinación seleccionada."
            )
        # Crear nueva colección
        new_collection = ProductCollection(
            line_id=line_id,
            subline_id=subline_id,
            target_id=target_id,
            last_type_id=last_type_id,
            code=code,
            aux_code=aux_code,
            name=name,
            description=description,
        )

        db.session.add(new_collection)

        return new_collection

    @staticmethod
    def patch_obj(obj: ProductCollection, data: dict) -> ProductCollection:
        dto = CollectionUpdateDTO(**data)
        col = CollectionService.patch_line(
            obj, dto.name, dto.description, dto.is_active
        )
        return col

    @staticmethod
    def patch_line(
        obj: ProductCollection,
        name: str = None,
        description: str = None,
        is_active: bool = None,
    ):
        if name:
            if obj.name != name:
                obj.name = name
        if description:
            obj.description = description

        if is_active is not None:
            obj.is_active = is_active

            db.session.query(Product).filter(Product.collection_id == obj.id).update(
                {Product.is_active: is_active}, synchronize_session="fetch"
            )

        if name is None and description is None and is_active is None:
            raise ValueError("No se proporciono un campo permitido")

        try:
            db.session.commit()
            return obj
        except Exception as e:
            current_app.logger.warning(f"error: {e}")
            db.session.rollback()
            raise str(e)

    @staticmethod
    def delete_obj(obj: ProductCollection):
        try:
            if obj.count_products > 0:
                raise IntegrityError("No se puede eliminar una colección con productos")
            db.session.delete(obj)
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.warning(f"error: {e}")
            db.session.rollback()
            raise str(e)


class ColorService:

    @staticmethod
    def get_obj_list(filters=None):
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
        return apply_filters(Color, filters)

    @staticmethod
    def get_obj(color_id):
        color = Color.query.get(color_id)
        if not color:
            raise NotFoundError("Color no encontrado")
        return color

    @staticmethod
    def create_obj(data):
        if Color.query.filter_by(code=data["code"]).first():
            raise ConflictError("Ya existe un color con ese código.")

        new_color = Color(
            code=data["code"].upper(),
            name=data["name"],
            hex_value=data.get("hex_value").upper(),
            description=data.get("description"),
        )
        db.session.add(new_color)
        try:
            db.session.commit()
            current_app.logger.info(f"Nuevo color guardado. {new_color.name}")
            return new_color
        except:
            db.session.rollback()
            current_app.logger.warning("Error al crear el color")
            raise

    @staticmethod
    def patch_obj(instance, data):
        if "name" in data:
            instance.name = data["name"].strip()
        if "code" in data:
            if Color.query.filter_by(code=data["code"]).first():
                raise ConflictError("Ya existe un color con ese código.")
            instance.code = data["code"].upper()
        if "hex_value" in data:
            instance.hex_value = data["hex_value"]
        if "description" in data:
            instance.description = data["description"]
        if "is_active" in data:
            instance.is_active = data["is_active"]

        try:
            db.session.commit()
            return instance
        except:
            db.session.rollback()
            current_app.logger.warning("Error al actualizar el recurso")
            raise

    @staticmethod
    def delete_obj(color):

        try:
            db.session.delete(color)
            db.session.commit()
            return True
        except Exception:
            raise


# **************************SIZE SERVICES*******************************************
class SizeService:

    @staticmethod
    def get_all_sizes(filters=None):
        query = Size.query
        if filters:
            if "serie" in filters:
                query = query.filter(Size.series_id == int(filters["serie"]))
            if "value" in filters:
                query = query.filter(Size.value == str(filters["value"]))

        return query.all()

    @staticmethod
    def get_sizes_from_serie(serie_id):
        sizes = Size.query.filter(Size.series_id == serie_id).all()
        return sizes

    @staticmethod
    def get_size(size_id):
        size = Size.query.get(size_id)
        if not size:
            raise NotFoundError("Plan de pago no encontrado")
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

        except Exception:
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


class LastService:

    @staticmethod
    def get_obj(id: int) -> Last | None:
        return db.session.get(Last, id)

    @staticmethod
    def get_obj_list(filters: dict = None) -> list[Last]:
        lasts = apply_filters(Last, filters)
        return lasts

    # helpers "hardcodeados" según tu operación
    def hardcoded_sizes() -> list[int]:
        # ajusta si tu empresa usa otro rango
        return list(range(14, 44))  # 14..43

    @staticmethod
    def sync_lasts() -> list[LastType]:
        """
        Crea las filas faltantes de LastTypes con sus Lasts para cada ProductCollection
        """
        session = db.session
        created: list[LastType] = []

        collections = session.query(ProductCollection).all()
        if not collections:
            return created

        sizes = LastService.hardcoded_sizes()
        lasts_types = session.query(LastType).all()
        collection_ids = {c.id for c in collections}
        lasttype_collection_ids = {lt.collection_id for lt in lasts_types}
        missing_ids = collection_ids - lasttype_collection_ids

        if not missing_ids:
            return created
        collection_name_by_id = {
            collection.id: collection.name for collection in collections
        }

        for cid in missing_ids:
            new_last_type = LastType(collection_id=cid, name=collection_name_by_id[cid])
            for size in sizes:
                new_last = Last(size=size, qty=0)
                new_last_type.lasts.append(new_last)
            created.append(new_last_type)
        session.add_all(created)

        try:
            session.commit()
            return created
        except IntegrityError:
            # Alguien pudo crear en paralelo; recargar estado y retornar vacío o recalcular
            session.rollback()
            # O bien, volver a calcular missing y crear solo los realmente faltantes…
            return []
        except SQLAlchemyError:
            session.rollback()
            raise

    @staticmethod
    def patch_obj(obj: Last, data: dict):
        """Actualiza uno o varios campo del objeto"""
        if data.get("qty"):
            obj.qty = data.get("qty")

        try:
            db.session.commit()
            return obj
        except Exception:
            db.session.rollback()
            raise


class LastTypeService:
    @staticmethod
    def get_obj(id: int) -> Last | None:
        return db.session.get(LastType, id)

    @staticmethod
    def create_obj(data: dict) -> LastType:
        from .dto_products import LastTypeDTO

        with db.session.begin():
            dto = LastTypeDTO(**data)
            new_last_type = LastTypeService.create_last_type(
                code=dto.code, name=dto.name, description=dto.description
            )
            return new_last_type

    @staticmethod
    def create_last_type(code: str, name: str, description: str) -> LastType:
        existing_code = db.session.query(LastType).filter_by(code=code).first()
        if existing_code:
            raise IntegrityError("Ya existe una familia de hormas con ese codigo")
        new_last_type = LastType(code=code, name=name, description=description)
        db.session.add(new_last_type)
        new_last_type.lasts = []

        # Generar hormas automaticamente

        lasts = []
        for s in range(14, 44):
            last = Last(family=new_last_type, size=s, qty=0)
            lasts.append(last)
        db.session.add_all(lasts)
        return new_last_type

    @staticmethod
    def get_obj_list(filters: dict = None) -> list[Last]:
        lasts = apply_filters(LastType, filters)
        return lasts

    @staticmethod
    def patch_obj(obj: LastType, data: dict):
        """Actualiza uno o varios campo del objeto"""

        if obj is None:
            raise NotFoundError("Objeto no encontrado")

        print("ingresa a patch lats")
        if data.get("code"):
            obj.code = data.get("code")

        try:
            db.session.commit()
            return obj
        except Exception:
            db.session.rollback()
            raise


class UpdateLifecycleStatusService:

    @staticmethod
    def update_status(instance, lifecyle_status: str):
        lifecyle_status = lifecyle_status.upper()
        from ..common.models import LifecycleStatus

        if lifecyle_status not in LifecycleStatus:
            raise ValidationError("El estado no tiene un valor valido")

        if lifecyle_status == "READY":
            if isinstance(instance, ProductVariant):
                UpdateLifecycleStatusService._validateVariant(instance)

            elif isinstance(instance, ProductDesign):
                UpdateLifecycleStatusService._validateDesign(instance)

            elif isinstance(instance, Product):
                UpdateLifecycleStatusService._validateProduct(instance)

            elif isinstance(instance, ProductCollection):
                UpdateLifecycleStatusService._validateCollection(instance)

        instance.lifecycle_status = lifecyle_status
        print("instance lifecycle status: ", instance.lifecycle_status)

        return instance

    @staticmethod
    def _validateVariant(instance: ProductVariant):
        if not instance.materials:
            raise ValidationError("Debe tener materiales asociados a la variante")

    @staticmethod
    def _validateDesign(instance: ProductDesign):
        if not instance.variants:
            raise ValidationError("Debe tener variantes asociadas al diseño")

        ready_variants = ProductVariant.query.filter_by(
            design_id=instance.id, lifecycle_status="READY"
        ).first()
        if ready_variants is None:
            raise ValidationError("Debe tener al menos una variante activa")

    @staticmethod
    def _validateProduct(instance: Product):
        if not instance.designs:
            raise ValidationError("Debe tener diseños asociados al producto")

        ready_designs = ProductDesign.query.filter_by(
            product_id=instance.id, lifecycle_status="READY"
        ).first()
        if ready_designs is None:
            raise ValidationError("Debe tener al menos un diseño activo")

    @staticmethod
    def _validateCollection(instance: ProductCollection):
        if not instance.last_type or not instance.last_type_id:
            raise ValidationError("Debe tener una horma asociada a la colección")
