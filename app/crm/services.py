from flask import current_app
from app import db

class CRMServices:

    @staticmethod
    def get_all_clients():
        from .models import Client
        clients = Client.query.all()
        return clients
    
    @staticmethod
    def get_client(client_id):
        from .models import Client
        client = Client.query.get_or_404(client_id)
        return client
    
    @staticmethod
    def get_client_by_ci(ci):
        from .models import Client
        client = Client.query.filter_by(ruc_or_ci=ci).first()
        return client
    
    @staticmethod
    def create_client(ruc_or_ci, name, client_type, address, city=None, email=None, phone=None):
        from .models import Client

        new_client = Client(ruc_or_ci = ruc_or_ci,
                            name = name,
                            client_type = client_type,
                            address = address,
                            city = city,
                            email = email,
                            phone = phone)

        try:
            db.session.add(new_client)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al guardar el cliente: {e}')

        return new_client
    

class LocationsServices:
    @staticmethod
    def get_provinces():
        from .models import Provinces
        provinces = Provinces.query.all()
        return provinces
    
    @staticmethod
    def get_province(province_id):
        from .models import Provinces
        province = Provinces.query.get_or_404(province_id)
        return province
    
    @staticmethod
    def get_cantons():
        from .models import Cantons
        cantons = Cantons.query.all()
        return cantons
    
    @staticmethod
    def get_canton(canton_id):
        from .models import Cantons
        canton = Cantons.query.get_or_404(canton_id)
        return canton