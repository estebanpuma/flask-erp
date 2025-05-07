# app/core/resources.py

from flask_restful import Resource, marshal
from flask import request, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import HTTPException

from .utils import success_response, error_response, validation_error_response


class HealthCheckResource(Resource):
    """
    Endpoint sencillo para probar si la API está corriendo.
    """
    def get(self):
        return success_response({"message": "API funcionando correctamente 🎯"})


class ProtectedResource(Resource):
    """
    Clase base para recursos protegidos con JWT.
    """
    method_decorators = [jwt_required()]


class AdminResource(ProtectedResource):
    """
    Clase base para recursos solo accesibles por administradores.
    """

    def dispatch_request(self, *args, **kwargs):
        current_user_id = get_jwt_identity()
        from app.admin.models import User
        user = User.query.get(current_user_id)
        if not user or user.role.name != 'admin':
            abort(403, description="Acceso denegado: solo administradores.")
        return super().dispatch_request(*args, **kwargs)


class BaseGetResource(Resource):
    schema_get = None       #servicio para obtener un elemento
    schema_list = None      #servicio para obtener una lista de elementos
    output_fields = None    #qué campos devolver(marshal)

    def get(self, resource_id=None):
        try:
            if resource_id:
                instance = self.schema_get(resource_id)
                if not instance:
                    return error_response("Recurso no encontrado", 404)
                return success_response(marshal(instance, self.output_fields))
            else:
                instances = self.schema_list()
                return success_response(marshal(instances, self.output_fields))

        except HTTPException as e:
            raise e
        except Exception as e:
            return error_response(f"Error inesperado: {str(e)}")


class BasePostResource(Resource):
    schema = None               #que campos deben ingresar 
    service_create = None       #servcio que creará un nuevo elemento
    output_fields = None        #que campos devolver

    def post(self):
        try:
            data = request.get_json()
            if not data:
                return error_response("No se enviaron datos", 400)

            errors = self.schema(data)
            if errors:
                return validation_error_response(errors)

            instance = self.service_create(**data)
            if not instance:
                return error_response("No se pudo crear el recurso", 400)

            return success_response(marshal(instance, self.output_fields), 201)

        except HTTPException as e:
            raise e
        except Exception as e:
            return error_response(f"Error inesperado: {str(e)}")


class BasePutResource(Resource):
    schema_validate = None          #que campos deben ingresar
    service_update = None           #servicio que actualizará todo el elemento
    output_fields = None            #que campos devolver

    def put(self, resource_id):
        try:
            data = request.get_json()
            if not data:
                return error_response("No se enviaron datos", 400)

            errors = self.schema_validate(data)
            if errors:
                return validation_error_response(errors)

            instance = self.service_update(resource_id, data)
            if not instance:
                return error_response("No se pudo actualizar el recurso", 400)

            return success_response(marshal(instance, self.output_fields))

        except HTTPException as e:
            raise e
        except Exception as e:
            return error_response(f"Error inesperado: {str(e)}")


class BaseDeleteResource(Resource):
    service_delete = None #servicio que elimina un elemento

    def delete(self, resource_id):
        try:
            success = self.service_delete(resource_id)
            if not success:
                return error_response("No se pudo eliminar el recurso", 400)

            return success_response({"message": "Recurso eliminado correctamente"})

        except HTTPException as e:
            raise e
        except Exception as e:
            return error_response(f"Error inesperado: {str(e)}")


class BasePatchResource(Resource):
    """
    Clase base para hacer actualizaciones parciales (PATCH) de recursos.
    """

    schema_validate_partial = None   # Validaciones opcionales
    service_patch = None             # Servicio que hará la actualización parcial
    output_fields = None             # Qué campos devolver (marshal)

    def patch(self, resource_id):
        try:
            data = request.get_json()
            if not data:
                return error_response("No se enviaron datos", 400)

            if self.schema_validate_partial:
                errors = self.schema_validate_partial(data)
                if errors:
                    return validation_error_response(errors)

            instance = self.service_patch(resource_id, data)
            if not instance:
                return error_response("No se pudo actualizar el recurso parcialmente", 400)

            return success_response(marshal(instance, self.output_fields))

        except HTTPException as e:
            raise e
        except Exception as e:
            current_app.logger.warning(f"errorrr {e}")
            return error_response(f"Error inesperado: {str(e)}")
