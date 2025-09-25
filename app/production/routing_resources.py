from flask_restful import Resource, request
from pydantic import ValidationError as PydValidationError

from ..core.exceptions import NotFoundError
from ..core.utils import error_response, success_response, validation_error_response
from .routing_service import OperationRoutingService


class RoutingPreviewResource(Resource):
    def post(self):
        try:
            data = request.get_json(force=True) or {}
            res = OperationRoutingService.preview(data)  # devuelve dict JSON-friendly
            # Es anidado (metrics.levels, nodes...), mejor no usar marshal aquí
            return success_response(res)
        except PydValidationError as e:
            return validation_error_response(str(e))
        except Exception as e:
            return error_response(f"Error en preview: {str(e)}", 400)


class RoutingGetResource(Resource):
    def get(self, resource_id):
        try:
            res = OperationRoutingService.get(model_id=resource_id)
            return success_response(res)
        except PydValidationError as e:
            return validation_error_response(str(e))
        except Exception as e:
            return error_response(f"Error: {str(e)}", 400)


class RoutingPostResource(Resource):
    def post(self):
        try:
            data = request.get_json(force=True) or {}
            res = OperationRoutingService.save(data)
            return success_response(res)
        except PydValidationError as e:
            return validation_error_response(str(e))
        except Exception as e:
            return error_response(f"Error al crear: {str(e)}", 400)


class RoutingDeleteResource(Resource):
    def delete(self, resource_id: int):
        try:
            ok = OperationRoutingService.delete(model_id=resource_id)
            return success_response({"ok": ok})
        except NotFoundError as e:
            return error_response(str(e), 404)
        except Exception as e:
            return error_response("Error inesperado: " + str(e), 500)
