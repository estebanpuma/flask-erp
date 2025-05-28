# app/core/resources.py
import inspect
from flask_restful import Resource, marshal
from flask import request, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import HTTPException
from .error_handlers import *
from sqlalchemy.exc import IntegrityError
from .utils import success_response, error_response, validation_error_response
from ..common.utils import ExcelImportService
import psycopg2

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
                    raise NotFoundError("Recurso no encontrado")  # usamos excepción personalizada
                return success_response(marshal(instance, self.output_fields))

            else:
                instances = self.schema_list()
                return success_response(marshal(instances, self.output_fields))

        except HTTPException as e:
            raise e  # errores de Flask siguen igual
        except NotFoundError as e:
            return error_response(str(e), 404)  # puedes dejarlo aquí o usar handler global
        except AppError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response("Error inesperado: " + str(e), 500)


class BasePostResource(Resource):
    schema = None               #que campos deben ingresar 
    service_create = None       #servcio que creará un nuevo elemento
    output_fields = None        #que campos devolver

    def post(self):
        try:
            data = request.get_json()
            if not data:
                return error_response("No se enviaron datos", 400)

            if self.schema:
                errors = self.schema(data)
                if errors:
                    return validation_error_response(errors)

            
            # 🔒 Contracto claro: data como dict completo
            instance = self.service_create(data)

            if not instance:
                return error_response("No se pudo crear el recurso", 400)

            if self.output_fields is None:
                return success_response(instance, 201)
            return success_response(marshal(instance, self.output_fields), 201)
            

        except HTTPException as e:
            raise e
        except IntegrityError as e:
            constraint = str(e)
            if isinstance(e.orig, psycopg2.errors.UniqueViolation):
                constraint = e.orig.diag.constraint_name 
            return error_response(f"Error de integridad: {str(constraint)}")
        except Exception as e:
            return error_response(f"Error inesperado: {str(e)}")
        except ValidationError as e:
            return error_response(f'Error de validacion: {str(e)}')
        


class BaseDeleteResource(Resource):
    service_delete = None #servicio que elimina un elemento
    service_get = None

    def delete(self, resource_id):
        try:
            if not self.service_get or not self.service_delete:
                raise AppError("Faltan servicios obligatorios en el recurso DELETE.")
            
            if self.service_get is None:
                # Llamar directamente al borrado si no se requiere instancia
                self.service_delete(resource_id)
            else:
                # Obtener instancia y luego borrar
                
                instance = self.service_get(resource_id)
                print(instance)
                deleted = self.service_delete(instance)

            if deleted:
                return success_response({"message": "Recurso eliminado correctamente"}, 200)
            else:
                return error_response("No se pudo eliminar el recurso", 400)

        except NotFoundError as e:
            return error_response(str(e), 404)
        except AppError as e:
            return error_response(str(e), 400)
        except HTTPException as e:
            raise e
        except Exception as e:
            return error_response(f"Error inesperado: {str(e)}", 500)


class BasePatchResource(Resource):
    """
    Clase base para hacer actualizaciones parciales (PATCH) de recursos.
    """

    schema_validate_partial = None         # Función que valida el input (data, instance)
    service_get = None            # Servicio que obtiene la instancia actual por ID
    service_patch = None          # Servicio que aplica cambios sobre la instancia
    output_fields = None                   # Campos a devolver

    def patch(self, resource_id):
        try:
            data = request.get_json()
            if not data:
                return error_response("No se enviaron datos", 400)

            if not self.service_get or not self.service_patch:
                raise AppError("Faltan servicios obligatorios en el recurso PATCH.")

            # Obtener instancia actual
            instance = self.service_get(resource_id)
            if not instance:
                raise NotFoundError("Recurso no encontrado")

            # Validación (si aplica)
            if self.schema_validate_partial:
                self.schema_validate_partial(data, instance)

            # Aplicar actualización
            updated = self.service_patch(instance, data)

            
            
            return success_response(marshal(updated, self.output_fields))

        except HTTPException as e:
            raise e
        except NotFoundError as e:
            return error_response(str(e), 404)
        except AppError as e:
            return error_response(str(e), 400)
        except Exception as e:
            current_app.logger.warning(f"Error inesperado: {e}")
            return error_response(f"Error inesperado: {str(e)}", 500)
        except ConflictError as e:
            return error_response(f"Error de conflicto de datos: {str(e)}", 500)
        
        


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
        


class BulkUploadBaseResource(Resource):
    """
    Recurso base para carga masiva desde archivo Excel.
    Espera que la subclase defina:
    - `import_service`: clase con método .process(file, row_handler)
    - `row_handler`: función que valida e inserta cada fila
    """

    import_service = None
    row_handler = None

    def post(self):
        try:
            if 'file' not in request.files:
                return error_response("No se encontró archivo Excel con clave 'file'.", 400)

            file = request.files['file']

            if not self.import_service or not self.row_handler:
                raise ValueError("Faltan componentes en la clase hija: 'import_service' y/o 'row_handler'.")

            result = self.import_service.process(file, self.row_handler)

            return success_response(result)

        except ValidationError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return error_response(f"Error inesperado: {str(e)}", 500)