from flask_restful import Resource, marshal, marshal_with, abort, request

from .services import CRMServices
from .schemas import client_fields

from .models import Client



class ClientSearchResource(Resource):

    @marshal_with(client_fields)
    def get(self):
        query = request.args.get('q', '').lower()

        try:
            results_by_ruc = Client.query.filter(Client.ruc_or_ci.ilike(f'%{query}%')).all()
            results_by_name = Client.query.filter(Client.name.ilike(f'%{query}%')).all()

            results = list({client.id: client for client in results_by_name + results_by_ruc}.values())
            
            return results, 200 
        
        except Exception as e:
            return str(e), 500


class ClientResource(Resource):

    @marshal_with(client_fields)
    def get(self, client_id=None):

        if client_id:
            client = CRMServices.get_client(client_id)
            return client, 200
        
        clients = CRMServices.get_all_clients()
        return clients, 200