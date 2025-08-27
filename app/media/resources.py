from flask_restful import Resource, marshal
from ..core.utils import success_response, error_response, validation_error_response
from flask import request, send_from_directory, current_app, abort
from ..core.exceptions import ValidationError, NotFoundError, ConflictError, AppError
from .schemas import general_image_fields
from .services import ImageService
from werkzeug.exceptions import HTTPException


class ImageListGetReource(Resource):
    def get(self, module:str, model_id:int):
        try:
            image_srv = ImageService()
            images = image_srv.list(module=module, model_id=model_id)
            return success_response(marshal(images, general_image_fields))

        except ValidationError as e: # ¡Primero las excepciones más específicas!
            # Aquí capturas tu ValidationError lanzado desde el servicio.
            # Puedes personalizar el mensaje o la estructura de la respuesta.
            return validation_error_response(str(e)) # O e.messages si es un diccionario/lista de Marshmallow

        except ConflictError as e:
            # Esta es la segunda excepción más específica que tienes, relacionada con la base de datos
            return error_response(f"Error de referecia", 400)
    
        except HTTPException as e:
            # Las excepciones de Flask/Werkzeug (como Abort) también son más específicas que Exception.
            # Puedes optar por relanzarlas para que sean manejadas por un manejador de errores global de Flask.
            raise e

        except Exception as e: # ¡Finalmente, la excepción más general!
            # Este es el último recurso para cualquier error no esperado.
            return error_response(f"Ha ocurrido un error interno inesperado: {str(e)}", 500)
    
    def post(self, module:str, model_id:int):
        try:
            files = request.files
            if files:
                img_svc = ImageService()
                # para cada campo declarado
                images = []
                for field_name, otr in files.items():
                    for fs in files.getlist(field_name):
                        img = img_svc.upload(module, model_id, fs,
                            is_primary=(fs.filename == request.form.get('primary')))
                        images.append(img)
                return success_response(marshal(images, general_image_fields), 200)
            else:
                return error_response('Sin atributo images', 500)
        except Exception as e:
            current_app.logger.warning(f'error: {e}')
            return error_response(str(e), 500)

class ImageResource(Resource):
    def get(self, module:str, filename:str):
        try:

            image_srv = ImageService()
            directory = image_srv.serve_media( module, filename)
            return send_from_directory(directory, filename)

        except ValidationError as e: # ¡Primero las excepciones más específicas!
            # Aquí capturas tu ValidationError lanzado desde el servicio.
            # Puedes personalizar el mensaje o la estructura de la respuesta.
            return validation_error_response(str(e)) # O e.messages si es un diccionario/lista de Marshmallow

        except ConflictError as e:
            # Esta es la segunda excepción más específica que tienes, relacionada con la base de datos
            return error_response(f"Error de referencia", 400)
    
        except HTTPException as e:
            # Las excepciones de Flask/Werkzeug (como Abort) también son más específicas que Exception.
            # Puedes optar por relanzarlas para que sean manejadas por un manejador de errores global de Flask.
            raise e

        except Exception as e: # ¡Finalmente, la excepción más general!
            # Este es el último recurso para cualquier error no esperado.
            return error_response(f"Ha ocurrido un error interno inesperado: {str(e)}", 500)
        

    def delete(self, module:str, image_id:int):
        image_svc = ImageService()
        try:
            image_svc.delete(module, image_id)
            return 'Imagen eliminada', 204
        except ValueError as e:
            abort(404, str(e))

