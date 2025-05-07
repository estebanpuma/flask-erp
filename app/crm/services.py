from sqlalchemy.exc import IntegrityError

from werkzeug.exceptions import NotFound, BadRequest

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
    def create_client(ruc_or_ci: str, name: str, client_type: str,
                      address: str, email: str, province_id: int, canton_id: int, phone: str = ''):
        from .models import Client

        # Validaciones previas
        #cantons_in_province = LocationsServices.get_cantons_by_province(province_id)
        canton = LocationsServices.get_canton(canton_id)

        if not canton or canton.province_id != province_id:
            raise ValueError('El cantón no pertenece a la provincia seleccionada.')

        # Crear el objeto Client
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

        # Guardar en la base de datos
        try:
            db.session.add(new_client)
            db.session.commit()
            return new_client

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning(f'Violación de integridad: {str(e)}')
            raise ValueError("Datos duplicados o inválidos.")
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error inesperado al guardar el cliente: {str(e)}')
            raise Exception("No se pudo crear el cliente por un error interno.")


    @staticmethod
    def update_client(client_id: int, data: dict):
        from .models import Client

        # 1. Buscar el cliente
        client = Client.query.get(client_id)
        if not client:
            raise NotFound("Cliente no encontrado.")

        # 2. Validaciones si se actualizan provincia o cantón
        province_id = data.get('province_id', client.province_id)
        canton_id = data.get('canton_id', client.canton_id)

        if 'province_id' in data or 'canton_id' in data:
            canton = LocationsServices.get_canton(canton_id)
            if not canton or canton.province_id != province_id:
                raise BadRequest('El cantón no pertenece a la provincia seleccionada.')

        # 3. Actualizar los campos (solo los que vienen en data)
        for field, value in data.items():
            if hasattr(client, field):
                setattr(client, field, value)

        # 4. Guardar cambios
        try:
            db.session.commit()
            return client

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning(f'Violación de integridad al actualizar cliente: {str(e)}')
            raise BadRequest("Datos duplicados o inválidos.")
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error inesperado al actualizar cliente: {str(e)}')
            raise Exception("No se pudo actualizar el cliente por un error interno.")

    
    def delete_client(client_id):
        from .models import Client
        client = Client.query.get(client_id)
        if not client:
            return False
        try:
            db.session.delete(client)
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning(f'Violacion de integridad al eliminar el cliente: {str(e)}')
            raise BadRequest('Datos comprometidos')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error inesperado al eliminar el cliente: {str(e)}')
            raise Exception('No se pudo eliminar el cliente')


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