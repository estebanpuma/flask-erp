from flask_restful import Resource, marshal_with, abort, request
from werkzeug.exceptions import HTTPException
from ..core.resources import BasePostResource, BasePatchResource, BaseDeleteResource, BaseGetResource, BasePutResource
from .services import CRMServices, LocationsServices
from .schemas import client_fields, province_fields, canton_fields
from .validations import validate_client_data, validate_client_partial_data

from .models import Client

from flask_jwt_extended import jwt_required, get_jwt_identity

from flask import current_app, jsonify, make_response
from flask_restful import Resource, reqparse


class ClientSearchResource(Resource):

    @marshal_with(client_fields)
    #@jwt_required()
    def get(self):
        query = request.args.get('q', '').lower()
        ci = request.args.get('ci', False)

        try:
            # Si buscan por cédula o RUC exacto
            if ci:
                client = CRMServices.get_client_by_ci(ci)
                if not client:
                    abort(404, message="Cliente no encontrado")
                return client, 200

            # Si buscan general
            if not query:
                abort(400, message="Debe ingresar un parámetro de búsqueda")

            # Unificar búsquedas en una sola consulta
            results = Client.query.filter(
                (Client.ruc_or_ci.ilike(f"%{query}%")) | (Client.name.ilike(f"%{query}%"))
            ).all()

            if not results:
                abort(404, message="No se encontraron clientes que coincidan")

            return results, 200

        except HTTPException as e:
            raise e

        except Exception as e:
            current_app.logger.error(f"Error en búsqueda de clientes: {str(e)}")
            abort(500, message="Error inesperado en la búsqueda")


class ClientGetResource(BaseGetResource):
    """
    Devuelve un cliente o una lista de clientes 
    """
    schema_get = staticmethod(CRMServices.get_client)       #servicio para obtener un elemento
    schema_list = staticmethod(CRMServices.get_all_clients)      #servicio para obtener una lista de elementos
    output_fields = client_fields


class ClientCreateResource(BasePostResource):
    """
    Crea un nuevo cliente en el sistema.
    """
    schema = staticmethod(validate_client_data)
    service_create = staticmethod(CRMServices.create_client)
    output_fields = client_fields
           

class ClientPatchResource(BasePatchResource):
    """
    Actualiza algun campo o campos especificos del cliente
    """
    schema_validate_partial = staticmethod(validate_client_partial_data)   # Validaciones opcionales
    service_patch = staticmethod(CRMServices.update_client)             # Servicio que hará la actualización parcial
    output_fields = client_fields            


class ClientDeleteResource(BaseDeleteResource):
    """
    Elimina un cliente (cuidado con las relaciones)
    """
    service_delete = staticmethod(CRMServices.delete_client)
    

class ProvinceResource(Resource):

    @marshal_with(province_fields)
    def get(self, province_id=None):
     
        try:

            if province_id:
                
                province = LocationsServices.get_province(province_id)

                return province, 200 if province else abort(404)
            
            provinces = LocationsServices.get_provinces()

            return provinces, 200 if provinces else abort(404)
        except Exception as e:
            abort(500, message=f'{str(e)}')


class CantonResource(Resource):

    @marshal_with(canton_fields)
    def get(self, canton_id=None):
     
        try:
            province_id = request.args.get('province_id', False)
            if province_id:
                cantons = LocationsServices.get_cantons_by_province(province_id)
                print(f'id: {province_id}')
                return cantons, 200 if cantons else abort(404)
            
            if canton_id:
                
                canton = LocationsServices.get_canton(canton_id)

                return canton, 200 if canton else abort(404)
            
            cantons = LocationsServices.get_cantons()

            return cantons, 200 if cantons else abort(404)
        except Exception as e:
            abort(500, message=f'{str(e)}')