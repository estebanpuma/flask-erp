from flask import current_app, request, send_from_directory
from flask_restful import Resource, marshal
from werkzeug.exceptions import HTTPException

from ..core.exceptions import ConflictError, ValidationError
from ..core.utils import error_response, success_response, validation_error_response
from .schemas import media_file_fields
from .services import ImageService


class MediaUploadResource(Resource):
    """
    Endpoint para subir uno o más archivos a un módulo específico.
    No asocia los archivos, solo los sube y crea los registros MediaFile.
    """

    def post(self, module: str):
        try:
            if "files" not in request.files:
                return error_response(
                    "No se encontraron archivos en la clave 'files'.", 400
                )

            files = request.files.getlist("files")
            if not files or files[0].filename == "":
                return error_response("No se seleccionó ningún archivo.", 400)

            uploaded_media = []
            with current_app.app_context():
                img_svc = ImageService()
                for file_storage in files:
                    media_file = img_svc.upload(module, file_storage)
                    uploaded_media.append(media_file)

            return success_response(marshal(uploaded_media, media_file_fields), 201)

        except (ValidationError, ValueError) as e:
            return validation_error_response(str(e))
        except Exception as e:
            current_app.logger.warning(f"error: {e}")
            return error_response(str(e), 500)


class MediaServeResource(Resource):
    """
    Endpoint seguro para servir archivos desde el directorio de uploads.
    """

    def get(self, module: str, filename: str):
        try:
            image_srv = ImageService()
            directory = image_srv.serve_media(module, filename)
            return send_from_directory(directory, filename)

        except ValidationError as e:
            return validation_error_response(str(e))
        except ConflictError:
            return error_response("Error de referencia", 400)
        except HTTPException as e:
            raise e
        except Exception as e:
            return error_response(
                f"Ha ocurrido un error interno inesperado: {str(e)}", 500
            )
