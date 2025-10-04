from flask import current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from app import db

from ..common.services import ProductCodeGenerator
from ..core.exceptions import ConflictError, NotFoundError, ValidationError
from ..core.filters import apply_filters
from ..core.utils import FileUploader
from .dto_lines import (
    CollectionCreateDTO,
    CollectionUpdateDTO,
    LineCreateDTO,
    LineUpdateDTO,
    SublineCreateDTO,
    SublineUpdateDTO,
)
from .dto_products import ProductCreateDTO, ProductDesignCreateDTO
from .entities import (
    PatchProductEntity,
    ProductVariantEntity,
    ProductVariantMaterialEntity,
)
from .models import (
    Color,
    Last,
    LastType,
    Product,
    ProductCollection,
    ProductDesign,
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

        with db.session.begin():
            dto = ProductCreateDTO(data)
            product = ProductService.create_product(
                target_id=dto.target_id,
                collection_id=dto.collection_id,
                name=dto.name,
                description=dto.description,
                line_id=dto.line_id,
                subline_id=dto.subline_id,
                designs=dto.designs,
                materials=dto.materials,
                variants=dto.variants,
            )
            return product

    @staticmethod
    def create_product(
        name: str,
        designs: list,
        variants: list,
        materials: list,
        line_id: int,
        target_id: int,
        collection_id: int,
        subline_id: int = None,
        description: str = None,
    ) -> Product:
        """Crea un nuevo producto (opcionalmente con un diseño)."""

        # validaciones
        line = LineService.get_obj(line_id)
        subline = None
        if subline_id is not None:
            subline = SublineService.get_obj(subline_id)
        target = TargetService.get_obj(target_id)
        collection = CollectionService.get_obj(collection_id)

        code = ProductCodeGenerator.get_next_model_code(
            linea=line, sublinea=subline, tipo=target, coleccion=collection
        )

        product = Product(
            code=code,
            name=name,
            line_id=line_id,
            subline_id=subline_id,
            target_id=target_id,
            collection_id=collection_id,
            description=description,
        )
        db.session.add(product)
        db.session.flush()  # Para obtener el ID

        current_app.logger.info(f" pos 0:{designs[0]}")
        # Si se proporcionan diseños, los crea Actualmente solo uno
        designs_data = []
        designs_data.append(designs[0])

        if designs_data:
            new_designs = DesignService.bulk_create_designs(product.id, designs_data)

        if variants:
            # Crear variantes para TODOS los diseños___ Atuamente solo uno

            variants = VariantService.bulk_create_variants(
                design_id=new_designs[0].id,
                design_code=new_designs[0].code,
                series_ids=variants[0].series_ids,
                materials=materials,
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

        if "line_id" in data:
            line = LineService.get_line(data["line_id"])
            if line is None:
                raise ValidationError("No existe liena con esa id")
        if "sub_line_id" in data:
            subline = SublineService.get_subline(data["sub_line_id"])
            if subline is None:
                raise ValidationError("N exise sublina con esa id")

        updated_product = PatchProductEntity(data).apply_changes(instance)
        try:
            db.session.commit()
            return updated_product
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
        EDITABLE_FIELDS = {"description", "name"}
        invalid_fields = set(data.keys()) - EDITABLE_FIELDS
        if invalid_fields:
            raise ValidationError(f"Campos no editables: {invalid_fields}")
        if "description" in data:
            instance.description = str(data["description"])
        if "name" in data:
            instance.name = str(data["name"])
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
        """Crea un diseño con sus variantes y materiales."""
        current_app.logger.info(f"dara:{data}")
        with db.session.begin():
            dto = ProductDesignCreateDTO(data)
            design = DesignService.create_design(
                product_id=dto.product_id,
                color_ids=dto.color_ids,
                # series_ids=dto.series_ids,
                name=dto.name,
                description=dto.description,
                variants=dto.variants,
                materials=dto.materials,
            )
            return design

    @staticmethod
    def create_design(
        product_id: int,
        color_ids: list[int],
        # series_ids:list[int],
        variants: list,
        materials: list,
        name: str = None,
        description: str = None,
    ) -> ProductDesign:
        """Funcion para crear un diseño con sus variantes y materiales."""

        product = Product.query.get(product_id)
        if not product:
            raise ValidationError(f"No existe el producto con id: {product_id}")

        color_ids = color_ids
        colors = []
        for color_id in color_ids:
            color = Color.query.get(color_id)
            if not color:
                raise ValidationError(f"No existe el color con id: {str(color_id)}")
            colors.append(color)

        colors_codes = [c.code.upper() for c in colors]
        color_part = "".join(colors_codes)
        c_code = f"{product.code}{str(color_part)}"
        # Genera el diseño
        design = ProductDesign(
            product_id=product_id, name=name, description=description, code=c_code
        )

        db.session.add(design)
        print(f"hasta aqui los designs: {design}")
        design.colors.extend(colors)
        db.session.flush()

        # Crea variantes para cada serie/talla
        VariantService.bulk_create_variants(
            design_id=design.id,
            design_code=design.code,
            series_ids=variants[0].series_ids,
            materials=materials,
        )

        from .pricing_service import PricingService

        PricingService(db.session).calculate_price(
            design_id=design.id,
            override_markup_pct=None,
            include_tax=False,
            force_recalc=True,
        )

        return design

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

            print(f"Colores en buldesing; {colors}")
            # Crear diseño (sin commit)
            design = ProductDesign(
                product_id=product_id,
                code=c_code,
            )
            print(f"desig en bulk desig : {design}")
            design.colors.extend(colors)
            current_app.logger.info(f"design.colors: {design.colors}")
            designs.append(design)

            # designs_and_materials.append({'design':design, 'materials':design_data.materials, "series_ids": design_data["series_ids"]})

        db.session.add_all(designs)

        # Flush para obtener IDs de diseños
        db.session.flush()

        return designs


class VariantService:

    @staticmethod
    def create_obj(data):
        return str("No se puede crear variantes individuales por el momento")

    @staticmethod
    def create_variants_obj(data):

        try:
            with db.session.begin():
                variants = VariantService.add_new_series_to_design(
                    design_id=data["design_id"],
                    series_ids=data["series_ids"],
                    materials=data["materials"],
                )
                return variants
        except Exception as e:
            current_app.logger.warning(f"Error al crear nuevas variantes. e{e}")
            raise e

    @staticmethod
    def bulk_create_variants(
        design_id: int, design_code: str, series_ids: list, materials: list
    ):
        """Crea todas las variantes para un diseño con sus materiales."""
        # Validación temprana de series (mejor performance)
        series = SizeSeries.query.filter(SizeSeries.id.in_(series_ids)).all()
        if len(series) != len(series_ids):
            missing_ids = set(series_ids) - {s.id for s in series}
            raise ValidationError(f"Series no encontradas: {missing_ids}")

        variants = []

        # Creación de todas las variantes primero
        for serie in series:
            serie_materials = materials  # Materiales compartidos para

            for size in serie.sizes:
                variant = ProductVariantEntity(
                    {
                        "design_id": design_id,
                        "size_id": size.id,
                        "design_code": design_code,
                        "size_value": size.value,
                        "materials": serie_materials,
                    }
                ).to_model()

                db.session.add(variant)
                variants.append(variant)

                # Asignar materiales específicos de la serie
                # no hago flush porque ya tengo la relacion SQLALchemy
                # no incluyo variant_id porque la relacion lo hace por mi
                for mat in serie_materials:
                    variant.materials.append(
                        ProductVariantMaterialDetail(
                            material_id=mat.material_id,
                            quantity=mat.quantity,
                        )
                    )

        return variants

    @staticmethod
    def add_new_series_to_design(
        design_id: int, series_ids: list, materials: list
    ) -> list[ProductVariant]:
        """Añade nuevas variantes a un diseño existente."""
        design = ProductDesign.query.get(design_id)
        if not design:
            raise ValidationError("No existe un diseno con el id indicado")
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
        except Exception:
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
        materials = ProductVariantMaterialDetail.query.filter(
            ProductVariantMaterialDetail.variant_id == variant_id
        ).all()
        return materials

    @staticmethod
    def create_obj(data):
        with db.session.begin():
            created_materials = ProductVariantMaterialService.create_variant_material(
                data
            )
            return created_materials

    @staticmethod
    def create_variant_material(data):
        """
        Crea objetos ProductVariantMaterialDetail para un variant_id dado.
        No hace commit, solo añade a la sesión.
        """
        ProductVariantMaterialService._check_foreign_keys(data)

        new_variant_materials = []

        for material in data["materials"]:

            obj = ProductVariantMaterialEntity(
                {
                    "variant_id": data["variant_id"],
                    "material_id": material["material_id"],
                    "quantity": material["quantity"],
                }
            ).to_model()
            new_variant_materials.append(obj)

        db.session.add_all(new_variant_materials)
        return new_variant_materials

    @staticmethod
    def patch_obj(instance, data: dict):
        EDITABLE_FIELDS = {"quantity"}
        invalid_fields = set(data.keys()) - EDITABLE_FIELDS
        if invalid_fields:
            raise ValidationError(f"Campos no editables: {invalid_fields}")

        if "quantity" in data:
            if data["quantity"] > 0:
                instance.quantity = data["quantity"]
            else:
                raise ValidationError("La cantidad debe ser mayor a 0")

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

        if not ProductVariant.query.get(data["variant_id"]):
            raise ValidationError("La variante no existe.")


class ProductVariantImageService:

    @staticmethod
    def get_images_by_variant(variant_id):
        pass

    # return ProductVariantImage.query.filter_by(variant_id=variant_id).all()

    @staticmethod
    def delete_image(image_id):
        pass
        # image = ProductVariantImage.query.get(image_id)
        # if not image:
        #    raise NotFoundError("Imagen no encontrada.")

        # Eliminar archivo físico (opcional)

    @staticmethod
    def create_image(variant_id, file):
        # Verificar que la variante exista
        if not ProductVariant.query.get(variant_id):
            raise NotFoundError("La variante no existe.")

        # Subir imagen usando el servicio genérico
        try:
            FileUploader.save_file(
                file=file, subfolder="products", entity_id=variant_id
            )
        except ValueError as e:
            raise ValidationError(str(e))

        # Registrar en base de datos
        image = None

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
        job = LineService.patch_line(obj, dto.name, dto.description)
        return job

    @staticmethod
    def patch_line(obj: ProductLine, name: str = None, description: str = None):
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
        job = SublineService.patch_subline(obj, dto.name, dto.description)
        return job

    @staticmethod
    def patch_subline(obj: ProductSubLine, name: str = None, description: str = None):
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
                line_id=dto.line_id,
                subline_id=dto.subline_id,
                target_id=dto.target_id,
                last_type_id=dto.last_type_id,
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
            query = db.session.query(ProductCollection).filter_by(code=code)

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
        col = CollectionService.patch_line(obj, dto.name, dto.description)
        return col

    @staticmethod
    def patch_line(
        obj: ProductCollection, name: str = None, description: str = NotImplemented
    ):
        print(name)
        print(obj.id)
        if name:
            if obj.name != name:
                obj.name = name
        if description:
            obj.description = description

        if not name and not description:
            raise ValueError("No se proporciono un campo permitido")

        try:
            db.session.commit()
            return obj
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
