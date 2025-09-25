import os

from flask import current_app
from werkzeug.utils import safe_join, secure_filename

from app import db

from ..core.exceptions import NotFoundError
from ..products.models import DesignImage, ProductImage


class ImageService:
    """
    Servicio genérico para subir, listar y eliminar imágenes de Products y Designs.
    """

    MODEL_MAP = {
        "products": (ProductImage, "product_id"),
        "designs": (DesignImage, "design_id"),
    }

    def __init__(self, storage=None):
        # Recupera la instancia de almacenamiento inyectada en app.extensions
        self.storage = storage or current_app.extensions["storage_service"]

    def _validate_and_save(self, module, file_storage):
        # Validaciones básicas
        if module not in self.MODEL_MAP:
            raise ValueError(f"Módulo no válido: {module}")
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

    def upload(self, module, model_id, file_storage, is_primary=False):
        with db.session.begin():
            # Guarda el archivo y crea el registro en BD
            saved_name = self._validate_and_save(module, file_storage)
            model_class, fk_field = self.MODEL_MAP[module]
            kwargs = {
                fk_field: model_id,
                "filename": saved_name,
                "file_path": f"/{module}/{saved_name}",
                "is_primary": is_primary,
            }
            img = model_class(**kwargs)
            db.session.add(img)
            print(f"this is img: {img}")
            return img

    def list(self, module, model_id):
        # Devuelve todos los registros de imagen para un modelo
        model_class, fk_field = self.MODEL_MAP[module]
        filter_kwargs = {fk_field: model_id}
        return model_class.query.filter_by(**filter_kwargs).all()

    def delete(self, module, image_id):
        # Elimina tanto el archivo como el registro en BD
        model_class, _ = self.MODEL_MAP[module]
        img = model_class.query.get(image_id)
        if not img:
            raise ValueError("Imagen no encontrada.")

        # Borra el archivo físico
        self.storage.delete(module, img.filename)
        # Borra el registro
        db.session.delete(img)
        db.session.commit()
        return True

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
