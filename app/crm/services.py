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
def create_client(ruc_or_ci: str,
                  name: str,
                  client_type: str,
                  address: str,
                  email: str,
                  province_id: int,
                  canton_id: int,
                  phone: str = ""):
    
    from .models import Client
    from flask import current_app

    try:
        # Verificar si ya existe el cliente
        existing = Client.query.filter_by(ruc_or_ci=ruc_or_ci).first()
        if existing:
            raise ValueError("Ya existe un cliente con este RUC/CI.")
        
        # Verificar que el cantón pertenezca a la provincia
        cantons_in_province = LocationsServices.get_cantons_by_province(province_id)
        canton = LocationsServices.get_canton(canton_id)

        if not canton or not any(c.id == canton_id for c in cantons_in_province):
            raise ValueError('El cantón no pertenece a la provincia seleccionada.')

        # Crear cliente
        new_client = Client(
            ruc_or_ci=ruc_or_ci,
            name=name,
            client_type=client_type,
            address=address,
            email=email,
            province_id=province_id,
            canton_id=canton_id,
            phone=phone
        )

        db.session.add(new_client)
        db.session.commit()
        return new_client
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.warning(f'Error al guardar el cliente: {e}')
        return None

    

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
    
    @staticmethod
    def get_cantons_by_province(province_id):
        from .models import Cantons, Provinces
        cantons = Cantons.query.filter(Cantons.province_id == province_id).all()
        return cantons