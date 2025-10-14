import os

from flask import current_app
from werkzeug.utils import safe_join, secure_filename

from app import db

from ..core.exceptions import NotFoundError, ValidationError
from ..products.models import ProductDesign
from .models import MediaFile


class ImageService:

    def __init__(self, storage=None):
        # Recupera la instancia de almacenamiento inyectada en app.extensions
        self.storage = storage or current_app.extensions["storage_service"]

    def _validate_and_save(self, module, file_storage):
        # Validaciones básicas
        if not file_storage:
            raise ValueError("No se proporcionó archivo.")

        filename = secure_filename(file_storage.filename)
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
            raise ValueError(f"Extensión no permitida: .{ext}")

        # Guarda el archivo y devuelve el nombre almacenado
        saved_name = self.storage.save(module, file_storage, filename)
        print(f"is saved: {saved_name}")
        return saved_name

    def upload(self, module, file_storage):
        """
        Sube un archivo, lo guarda y crea un registro MediaFile genérico.
        No lo asocia a ningún modelo específico todavía.
        """
        # Asegura que el nombre del archivo sea seguro
        filename = secure_filename(file_storage.filename)

        # 1. Verificar si ya existe un archivo con este nombre en el módulo.
        existing_file = (
            db.session.query(MediaFile)
            .filter_by(filename=filename, module=module)
            .first()
        )
        if existing_file:
            # Si ya existe, simplemente lo retornamos. No creamos uno nuevo.
            return existing_file
        print("imageSerivce: ", existing_file)
        # 2. Si no existe, procedemos con la creación normal.
        saved_name = self._validate_and_save(module, file_storage)
        media_file = MediaFile(
            filename=saved_name,
            file_path=f"/{module}/{saved_name}",
            module=module,
            mime_type=file_storage.mimetype,
            size=file_storage.content_length,
        )
        db.session.add(media_file)
        db.session.flush()  # Hacemos flush para asegurarnos de que el objeto tiene un ID antes de retornarlo.
        return media_file

    def associate_images_to_design(self, design_id, media_ids, primary_media_id=None):
        """Asocia una lista de MediaFiles a un ProductDesign."""
        design = db.session.get(ProductDesign, design_id)
        if not design:
            raise NotFoundError(f"Diseño con ID {design_id} no encontrado.")

        media_files = (
            db.session.query(MediaFile).filter(MediaFile.id.in_(media_ids)).all()
        )
        if len(media_files) != len(media_ids):
            raise ValidationError("Uno o más IDs de imágenes no son válidos.")

        # Obtener el orden máximo actual para continuar desde ahí
        max_order = (
            db.session.query(db.func.max(db.table("product_design_images").c.order))
            .filter_by(design_id=design.id)
            .scalar()
            or -1
        )

        # No se limpian las asociaciones viejas, solo se añaden las nuevas
        # design.images.clear()
        for i, media_file in enumerate(media_files, start=1):
            is_primary = (
                primary_media_id is not None and media_file.id == primary_media_id
            )
            # Si no hay imágenes, la primera que se sube es primaria
            if not design.images and i == 1 and primary_media_id is None:
                is_primary = True

            # Esta es una forma de añadir a una tabla de asociación con campos extra
            from ..products.models import ProductDesignImage

            association = ProductDesignImage(
                design_id=design.id,
                media_file_id=media_file.id,
                is_primary=is_primary,
                order=max_order + i,
            )
            db.session.add(association)

    def delete(self, module, image_id):
        # Elimina tanto el archivo como el registro en BD
        img = db.session.get(MediaFile, image_id)
        if not img:
            raise ValueError("Imagen no encontrada.")

        # Borra el archivo físico
        self.storage.delete(module, img.filename)
        # Borra el registro
        try:
            db.session.delete(img)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise

    def serve_media(self, module, filename):
        # 1) Validar módulo
        if module not in current_app.config["UPLOAD_FOLDERS"]:
            raise NotFoundError("Modulo no encontrado")

        # 2) Construir path de forma segura
        directory = current_app.config["UPLOAD_FOLDERS"][module]
        safe_path = safe_join(directory, filename)
        if not safe_path or not os.path.isfile(safe_path):
            raise NotFoundError("Archivo no encontrado")
        # 3) Servir el archivo
        return directory
