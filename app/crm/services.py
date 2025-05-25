from sqlalchemy.exc import IntegrityError

from werkzeug.exceptions import NotFound, BadRequest

from flask import current_app
from app import db

from ..core.filters import apply_filters
from ..core.error_handlers import *

from ..common.utils import ExcelImportService

from .entities import ClientEntity, ClientCategoryEntity, ContactEntity

from ..common.parsers import parse_bool, parse_int, parse_str


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

        entity = ClientEntity(data)  # Valida datos

        CRMServices._validate_province_canton_relationship(entity.province_id, entity.canton_id)

        CRMServices._check_foreign_keys(data)

        if Client.query.filter_by(ruc_or_ci=entity.ruc_or_ci).first():
            raise ConflictError("RUC o cédula ya registrada.")
        # Crear el objeto Client
        new_client = Client(
            name=entity.name,
            ruc_or_ci=entity.ruc_or_ci,
            phone=entity.phone,
            email=entity.email,
            address=entity.address,
            province_id=entity.province_id,
            canton_id=entity.canton_id,
            client_type=entity.client_type,
            client_category_id=entity.client_category_id,
            is_special_taxpayer=entity.is_special_taxpayer or False
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

        # 1. No permitir cambiar el RUC
        if 'ruc_or_ci' in data:
            raise ValidationError("No se puede modificar el RUC o cédula.")

        # 2. Fusionar datos actuales con nuevos (defensivamente)
        merged_data = {
            'name': data.get('name', instance.name),
            'ruc_or_ci': instance.ruc_or_ci,
            'email': data.get('email', instance.email),
            'phone': data.get('phone', instance.phone),
            'address': data.get('address', instance.address),
            'province_id': data.get('province_id', instance.province_id),
            'canton_id': data.get('canton_id', instance.canton_id),
            'is_special_taxpayer': data.get('is_special_taxpayer', instance.is_special_taxpayer),
            'client_type': data.get('client_type', instance.client_type),
            'client_category_id': data.get('client_category_id', instance.client_category_id)
        }

        # 3. Validar con entidad
        entity = ClientEntity(merged_data, is_update=True)

        # 4. Validaciones de clave foránea y consistencia entre canton/provincia
        CRMServices._check_foreign_keys(merged_data)
        CRMServices._validate_province_canton_relationship(entity.province_id, entity.canton_id)

        # 5. Actualizar atributos
        for key, value in data.items():
            setattr(instance, key, value)

        # 6. Guardar cambios
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
        from .models import Cantons, Provinces, ClientCategory
        province_id = parse_int(data.get("province_id"))
        canton_id = parse_int(data.get("canton_id"))
        client_category_id = parse_int(data.get("client_category_id"))

        if province_id and not Provinces.query.get(province_id):
            raise ValidationError("Provincia no encontrada.")

        if canton_id and not Cantons.query.get(canton_id):
            raise ValidationError("Cantón no encontrado.")

        if client_category_id and not ClientCategory.query.get(client_category_id):
            raise ValidationError("Categoría de cliente no encontrada.")
        
    def _validate_province_canton_relationship(province_id, canton_id):
        from .models import Cantons, Provinces
        canton = Cantons.query.get(canton_id)
        if not canton:
            raise ValidationError("Cantón no encontrado.")
        if not Provinces.query.get(province_id):
            raise ValidationError("Provincia no encontrada.")
        if canton.province_id != province_id:
            raise ValidationError("El cantón no pertenece a la provincia seleccionada.")
        
    @staticmethod
    def create_from_excel_row(data):
        from .entities import ClientEntity
        from .models import Client, Provinces, Cantons, ClientCategory

        entity = ClientEntity(data)

        # Validaciones foráneas
        if entity.province_id and not Provinces.query.get(entity.province_id):
            raise ValidationError("Provincia no encontrada.")
        if entity.canton_id and not Cantons.query.get(entity.canton_id):
            raise ValidationError("Cantón no encontrado.")
        if entity.client_category_id and not ClientCategory.query.get(entity.client_category_id):
            raise ValidationError("Categoría no encontrada.")

        # Validación de duplicados
        if Client.query.filter_by(ruc_or_ci=entity.ruc_or_ci).first():
            raise ValidationError(f"Ya existe cliente con RUC/Cédula {entity.ruc_or_ci}")

        client = Client(
            name=entity.name,
            ruc_or_ci=entity.ruc_or_ci,
            phone=entity.phone,
            email=entity.email,
            address=entity.address,
            province_id=entity.province_id,
            canton_id=entity.canton_id,
            client_type=entity.client_type,
            client_category_id=entity.client_category_id,
            is_special_taxpayer=entity.is_special_taxpayer or False
        )

        db.session.add(client)
        return client
        

class ClientBulkUploadService(ExcelImportService):

    required_columns = [
        "name", "ruc_or_ci", "phone", "client_type", "address", "province_id", "canton_id"
    ]

    @staticmethod
    def handle_row(data):
        return CRMServices.create_from_excel_row(data)  # esta función agrega y valida, pero no hace commit



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
        


class ContactService:
    

    def get_obj(contact_id):
        from .models import Contact
        obj = Contact.query.get(contact_id)
        if not obj:
            raise NotFoundError("Contacto no encontrado.")
        return obj

    def get_obj_list(filters=None):
        from .models import Contact
        return apply_filters(Contact, filters)

    def create_obj(data):
        from .models import Contact, Client, ClientCategory
        entity = ContactEntity(data)

        if not Client.query.get(entity.client_id):
            raise ValidationError("Cliente no encontrado.")

        contact = Contact(
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            position=entity.position,
            notes=entity.notes,
            birth_date=entity.birth_date,
            client_id=entity.client_id
        )

        db.session.add(contact)
        db.session.commit()
        return contact

    def patch_obj(contact, data):
        merged_data = {
            "name": data.get("name", contact.name),
            "email": data.get("email", contact.email),
            "phone": data.get("phone", contact.phone),
            "position": data.get("position", contact.position),
            "notes": data.get("notes", contact.notes),
            "birth_date": data.get("birth_date", contact.birth_date),
            "client_id": data.get("client_id", contact.client_id),
        }

        entity = ContactEntity(merged_data)

        for k, v in data.items():
            setattr(contact, k, v)

        db.session.commit()
        return contact

    def delete_obj(contact):
        db.session.delete(contact)
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e