# app/core/utils.py

from flask import jsonify, make_response

from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy import or_

# utils/file_uploader.py

import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


class FileUploader:
    """
    Servicio genérico para subir archivos a la carpeta /static/media/
    Compatible con módulos: productos, clientes, usuarios, etc.
    """

    @staticmethod
    def save_file(file, subfolder: str, entity_id: int = None) -> str:
        """
        Guarda un archivo en la carpeta correspondiente.

        Args:
            file: objeto werkzeug.datastructures.FileStorage
            subfolder: clave del módulo (products, clients, etc.)
            entity_id: opcional, para crear subcarpeta por entidad (ej: cliente_id, variant_id)

        Returns:
            Ruta pública accesible del archivo: /static/media/<subfolder>/<entity_id>/<file>
        """
        if not file:
            raise ValueError("Archivo no recibido.")
        if file.filename == '':
            raise ValueError("Nombre de archivo vacío.")

        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
            raise ValueError("Extensión de archivo no permitida.")

        # Generar nombre seguro y único
        original_name = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}.{ext}"

        # Construir carpeta de destino
        base_folder = current_app.config["UPLOAD_FOLDERS"].get(subfolder)
        if not base_folder:
            raise ValueError(f"Subcarpeta no válida: {subfolder}")

        if entity_id:
            target_folder = os.path.join(base_folder, str(entity_id))
        else:
            target_folder = os.path.join(base_folder, uuid.uuid4().hex[:8])

        os.makedirs(target_folder, exist_ok=True)

        full_path = os.path.join(target_folder, unique_name)
        file.save(full_path)

        # Convertir a ruta pública
        relative = full_path.split("static")[-1].replace(os.sep, "/")
        return f"/static{relative}"


def apply_filters(model, filters: dict):
    query = model.query
    for field, value in filters.items():
        if not hasattr(model, field):
            continue  # ignorar campos inválidos
        column: InstrumentedAttribute = getattr(model, field)

        if isinstance(value, str) and "%" in value:
            query = query.filter(column.ilike(value))
        elif isinstance(value, str) and value.startswith("~"):  # filtro "contiene"
            query = query.filter(column.ilike(f"%{value[1:]}%"))
        else:
            query = query.filter(column == value)

    return query.all()


def success_response(data=None, status_code=200):
    """
    Estandariza respuestas exitosas.
    """
    if data is None:
        data = {"message": "Operación exitosa"}
    return make_response(jsonify(data), status_code)


def error_response(message="Error inesperado", status_code=500):
    """
    Estandariza respuestas de error.
    """
    return make_response(jsonify({"message": message}), status_code)

def validation_error_response(errors):
    """
    Devuelve un error específico de validación.
    """
    return make_response(jsonify({"message": errors}), 400)
