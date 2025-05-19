from sqlalchemy.exc import IntegrityError

from werkzeug.exceptions import NotFound, BadRequest

from flask import current_app
from app import db

from ..core.filters import apply_filters
from ..core.error_handlers import *

from .entities import ClientEntity, ClientCategoryEntity


class ClientCategoryService:
    @staticmethod
    def get_obj_list(filters=None):
        from .models import ClientCategory
        
        return apply_filters(ClientCategory, filters)
    
    @staticmethod
    def get_obj(id):
        from .models import ClientCategory
        category = ClientCategory.query.get(id)
        if not category:
            raise NotFoundError('Categoria no encontrada')
        return category

    @staticmethod
    def create_obj(data:dict):
        from .models import ClientCategory
        entity = ClientCategoryEntity(data)  # Valida datos

        if ClientCategory.query.filter_by(name=entity.name).first():
            raise ConflictError("Categoría ya registrada.")
        # Crear el objeto Client
        new_category = ClientCategory(
            name=entity.name,
            description=entity.description,
        )

        # Guardar en la base de datos
        try:
            db.session.add(new_category)
            db.session.commit()
            return new_category

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning(f'Violación de integridad: {str(e)}')
            raise ValueError("Datos duplicados o inválidos.")
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error inesperado al guardar categoria: {str(e)}')
            raise Exception("No se pudo crear categoria por un error interno.")


    @staticmethod
    def patch_obj(instance, data: dict):
        

        merged_data = {
            'name': data.get('name', instance.name),
            'description': instance.description,  
        }
        entity = ClientCategoryEntity(merged_data)

        for k, v in data.items():
            setattr(instance, k, v)
      
        try:
            db.session.commit()
            return instance

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning(f'Violación de integridad al actualizar categoría: {str(e)}')
            raise BadRequest("Datos duplicados o inválidos.")
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error inesperado al actualizar categoría: {str(e)}')
            raise Exception("No se pudo actualizar categoría por un error interno.")

    
    def delete_obj(id):
        from .models import ClientCategory
        category = ClientCategory.query.get(id)
        if not category:
            return False
        try:
            db.session.delete(category)
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning(f'Violacion de integridad al eliminar categoria: {str(e)}')
            raise BadRequest('Datos comprometidos')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error inesperado al eliminar categoria: {str(e)}')
            raise Exception('No se pudo eliminar categoria')

        

class CRMServices:

    @staticmethod
    def get_obj_list(filters=None):
        from .models import Client
        
        return apply_filters(Client, filters)
    
    @staticmethod
    def get_obj(client_id):
        from .models import Client
        client = Client.query.get(client_id)
        if not client:
            raise NotFoundError('Cliente no encontrado')
        return client

    @staticmethod
    def create_obj(data:dict):
        from .models import Client

        # Validaciones previas
        #cantons_in_province = LocationsServices.get_cantons_by_province(province_id)
        canton = LocationsServices.get_canton(data['canton_id'])

        if not canton or canton.province_id != data['province_id']:
            raise ValueError('El cantón no pertenece a la provincia seleccionada.')

        entity = ClientEntity(data)  # Valida datos

        CRMServices._check_foreign_keys(data)

        if Client.query.filter_by(ruc_or_ci=entity.ruc_or_ci).first():
            raise ConflictError("RUC o cédula ya registrada.")
        # Crear el objeto Client
        new_client = Client(
            ruc_or_ci=data['ruc_or_ci'],
            name=data['name'],
            client_type=data['client_type'],
            address=data['address'],
            email=data['email'],
            province_id=data['province_id'],
            canton_id=data['canton_id'],
            phone=data.get('phone')
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
    def patch_obj(instance, data: dict):
        
        # 2. Validaciones si se actualizan provincia o cantón
        province_id = data.get('province_id', instance.province_id)
        canton_id = data.get('canton_id', instance.canton_id)

        if 'province_id' in data or 'canton_id' in data:
            canton = LocationsServices.get_canton(canton_id)
            if not canton or canton.province_id != province_id:
                raise BadRequest('El cantón no pertenece a la provincia seleccionada.')

        if 'ruc_or_ci' in data:
            raise ValidationError("No se puede modificar el RUC o cédula.")

        merged_data = {
            'name': data.get('name', instance.name),
            'ruc_or_ci': instance.ruc_or_ci,  # inmutable
            'email': data.get('email', instance.email),
            'phone': data.get('phone', instance.phone),
            'address': data.get('address', instance.address),
            'province_id': data.get('province_id', instance.province_id),
            'canton_id': data.get('canton_id', instance.canton_id),
            'is_special_taxpayer': data.get('is_special_taxpayer', instance.is_special_taxpayer),
            'client_type': data.get('client_type', instance.client_type),
            'client_category_id': data.get('client_category_id', instance.client_category_id)
        }
        entity = ClientEntity(merged_data, is_update=True)

        CRMServices._check_foreign_keys(data)

        for k, v in data.items():
            setattr(instance, k, v)

        # 4. Guardar cambios
        try:
            db.session.commit()
            return instance

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning(f'Violación de integridad al actualizar cliente: {str(e)}')
            raise BadRequest("Datos duplicados o inválidos.")
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error inesperado al actualizar cliente: {str(e)}')
            raise Exception("No se pudo actualizar el cliente por un error interno.")

    
    def delete_obj(client_id):
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
        
    @staticmethod
    def _check_foreign_keys(data):
        from .models import Cantons, Provinces
        if not Cantons.query.get(data["canton_id"]):
            raise ValidationError("Canton no válido.")
        if not Provinces.query.get(data["province_id"]):
            raise ValidationError("Provincia no válida.")
        


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
    

class CantonService:

    @staticmethod
    def get_obj(id):
        from .models import Cantons
        canton = Cantons.query.get(id)
        if not canton:
            raise NotFoundError('El canton no existe')
        
        return canton
    

    @staticmethod
    def get_obj_list(filters=None):
        from .models import Cantons
        return apply_filters(Cantons, filters)
    

    def patch_obj(instance, data):
        
        setattr(instance, 'population', data.get('description'))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        

class ProvinceService:

    @staticmethod
    def get_obj(id):
        from .models import Provinces
        province = Provinces.query.get(id)
        if not province:
            raise NotFoundError('La provincia no existe no existe')
        return province
    
    @staticmethod
    def get_obj_list(filters=None):
        from .models import Provinces
        return apply_filters(Provinces, filters)
    

    def patch_obj(instance, data):
        
        setattr(instance, 'population', data.get('description'))

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e