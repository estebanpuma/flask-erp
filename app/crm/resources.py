from flask_restful import Resource, marshal, marshal_with, abort, request
from werkzeug.exceptions import HTTPException

from flask import flash
from .services import CRMServices, LocationsServices
from .schemas import client_fields, province_fields, canton_fields

from .models import Client



class ClientSearchResource(Resource):

    @marshal_with(client_fields)
    def get(self):
        query = request.args.get('q', '').lower()
        ci = request.args.get('ci', False)
        
        try:
            if ci:
                result = CRMServices.get_client_by_ci(ci)
                if result is None:
                    abort(404, message="User not found")
                return result, 200

            results_by_ruc = Client.query.filter(Client.ruc_or_ci.ilike(f'%{query}%')).all()
            results_by_name = Client.query.filter(Client.name.ilike(f'%{query}%')).all()

            results = list({client.id: client for client in results_by_name + results_by_ruc}.values())
            
            return results, 200 
        
        except HTTPException as e:  # Excepciones de Flask
            raise e
        
        except Exception as e:  # Excepciones específicas
            abort(500, message="Error de base de datos")


class ClientResource(Resource):

    @marshal_with(client_fields)
    def get(self, client_id=None):

        if client_id:
            client = CRMServices.get_client(client_id)
            return client, 200
        
        clients = CRMServices.get_all_clients()
        return clients, 200
    

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