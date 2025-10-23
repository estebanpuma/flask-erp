from flask import current_app
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload  # Importa joinedload
from werkzeug.exceptions import BadRequest

from app import db

from ..common.parsers import parse_int
from ..common.utils import ExcelImportService
from ..core.error_handlers import ConflictError, NotFoundError, ValidationError
from ..core.filters import apply_filters
from .entities import ClientCategoryEntity, ClientEntity
from .models import Client, Contact


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
            raise NotFoundError("Categoria no encontrada")
        return category

    @staticmethod
    def create_obj(data: dict):
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
            current_app.logger.warning(f"Violación de integridad: {str(e)}")
            raise ValueError("Datos duplicados o inválidos.")

        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(
                f"Error inesperado al guardar categoria: {str(e)}"
            )
            raise Exception("No se pudo crear categoria por un error interno.")

    @staticmethod
    def patch_obj(instance, data: dict):

        merged_data = {
            "name": data.get("name", instance.name),
            "description": instance.description,
        }
        ClientCategoryEntity(merged_data)

        for k, v in data.items():
            setattr(instance, k, v)

        try:
            db.session.commit()
            return instance

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning(
                f"Violación de integridad al actualizar categoría: {str(e)}"
            )
            raise BadRequest("Datos duplicados o inválidos.")

        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(
                f"Error inesperado al actualizar categoría: {str(e)}"
            )
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
            current_app.logger.warning(
                f"Violacion de integridad al eliminar categoria: {str(e)}"
            )
            raise BadRequest("Datos comprometidos")
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(
                f"Error inesperado al eliminar categoria: {str(e)}"
            )
            raise Exception("No se pudo eliminar categoria")


class CRMServices:

    @staticmethod
    def search_clients(query: str, limit=10):
        from .models import Client, ClientCategory, Provinces

        q = query.strip().lower()
        clients = (
            db.session.query(
                Client.id,
                Client.name,
                Client.ruc_or_ci,
                Client.address,
                Client.phone,
                Client.province_id,
                Client.canton_id,
                func.coalesce(ClientCategory.name, "Sin categoría").label(
                    "client_category"
                ),
                Provinces.name.label("province_name"),
            )
            .join(
                Provinces,
                Client.province_id == Provinces.id,
            )
            .outerjoin(ClientCategory, Client.client_category_id == ClientCategory.id)
            .filter((Client.name.ilike(f"%{q}%")) | (Client.ruc_or_ci.ilike(f"%{q}%")))
            .order_by(Client.name.asc())
            .limit(limit)
            .all()
        )
        return clients

    @staticmethod
    def get_obj_list(filters: dict = None):
        print("servicios ")
        filtered = apply_filters(Client, filters)
        print("filtered: ", filtered)
        return filtered

    @staticmethod
    def get_obj(client_id: int):
        client = Client.query.options(
            joinedload(Client.canton), joinedload(Client.province)
        ).get(client_id)
        if not client:
            raise NotFoundError("Cliente no encontrado")
        return client

    @staticmethod
    def create_obj(data: dict):
        from .models import Client

        entity = ClientEntity(data)  # Valida datos

        CRMServices._validate_province_canton_relationship(
            entity.province_id, entity.canton_id
        )

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
            is_special_taxpayer=entity.is_special_taxpayer or False,
        )

        # Guardar en la base de datos
        try:
            db.session.add(new_client)
            db.session.commit()
            return new_client

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning(f"Violación de integridad: {str(e)}")
            raise ValueError("Datos duplicados o inválidos.")

        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(
                f"Error inesperado al guardar el cliente: {str(e)}"
            )
            raise Exception("No se pudo crear el cliente por un error interno.")

    @staticmethod
    def patch_obj(instance: Client, data: dict):

        from .dto import ClientPatchDTO

        dto = ClientPatchDTO.model_validate(data)
        if dto.name is not None:
            instance.name = dto.name
        if dto.ruc_or_ci is not None:
            instance.ruc_or_ci = dto.ruc_or_ci
        if dto.client_type is not None:
            instance.client_type = dto.client_type
        if dto.province_id is not None:
            instance.province_id = dto.province_id

        if dto.canton_id is not None:
            instance.canton_id = dto.canton_id

        if dto.address is not None:
            instance.address = dto.address

        if dto.client_category_id is not None:
            instance.client_category_id = dto.client_category_id
        if dto.is_special_taxpayer is not None:
            instance.is_special_taxpayer = dto.is_special_taxpayer

        try:
            db.session.commit()
            return instance

        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.warning(
                f"Violación de integridad al actualizar cliente: {str(e)}"
            )
            raise BadRequest("Datos duplicados o inválidos.")

        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(
                f"Error inesperado al actualizar cliente: {str(e)}"
            )
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
            current_app.logger.warning(
                f"Violacion de integridad al eliminar el cliente: {str(e)}"
            )
            raise BadRequest("Datos comprometidos")
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(
                f"Error inesperado al eliminar el cliente: {str(e)}"
            )
            raise Exception("No se pudo eliminar el cliente")

    @staticmethod
    def _check_foreign_keys(data):
        from .models import Cantons, Provinces

        province_id = parse_int(data.get("province_id"))
        canton_id = parse_int(data.get("canton_id"))
        # client_category_id = parse_int(data.get("client_category_id"))

        if province_id and not Provinces.query.get(province_id):
            raise ValidationError("Provincia no encontrada.")

        if canton_id and not Cantons.query.get(canton_id):
            raise ValidationError("Cantón no encontrado.")

        # if client_category_id and not ClientCategory.query.get(client_category_id):
        # raise ValidationError("Categoría de cliente no encontrada.")

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
        from .models import Cantons, Client, ClientCategory, Provinces

        entity = ClientEntity(data)

        # Validaciones foráneas
        if entity.province_id and not Provinces.query.get(entity.province_id):
            raise ValidationError("Provincia no encontrada.")
        if entity.canton_id and not Cantons.query.get(entity.canton_id):
            raise ValidationError("Cantón no encontrado.")
        if entity.client_category_id and not ClientCategory.query.get(
            entity.client_category_id
        ):
            raise ValidationError("Categoría no encontrada.")

        # Validación de duplicados
        if Client.query.filter_by(ruc_or_ci=entity.ruc_or_ci).first():
            raise ValidationError(
                f"Ya existe cliente con RUC/Cédula {entity.ruc_or_ci}"
            )

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
            is_special_taxpayer=entity.is_special_taxpayer or False,
        )

        db.session.add(client)
        return client


class ClientBulkUploadService(ExcelImportService):

    required_columns = [
        "name",
        "ruc_or_ci",
        "phone",
        "client_type",
        "address",
        "province_id",
        "canton_id",
    ]

    @staticmethod
    def handle_row(data):
        return CRMServices.create_from_excel_row(
            data
        )  # esta función agrega y valida, pero no hace commit


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
        from .models import Cantons

        cantons = Cantons.query.filter(Cantons.province_id == province_id).all()
        return cantons


class CantonService:

    @staticmethod
    def get_obj(id):
        from .models import Cantons

        canton = Cantons.query.get(id)
        if not canton:
            raise NotFoundError("El canton no existe")

        return canton

    @staticmethod
    def get_obj_list(filters=None):
        from .models import Cantons

        return apply_filters(Cantons, filters)

    def patch_obj(instance, data):

        setattr(instance, "population", data.get("description"))

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
            raise NotFoundError("La provincia no existe no existe")
        return province

    @staticmethod
    def get_obj_list(filters=None):
        from .models import Provinces

        return apply_filters(Provinces, filters)

    def patch_obj(instance, data):

        setattr(instance, "population", data.get("description"))

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

    @staticmethod
    def create_obj(data: dict):
        from .dto import ContactCreateDTO

        with db.session.begin():
            dto = ContactCreateDTO.model_validate(data)
            new_contact = ContactService.create_contact(
                name=dto.name,
                client_id=dto.client_id,
                email=dto.email,
                phone=dto.phone,
                position=dto.position,
                notes=dto.notes,
                birth_date=dto.birth_date,
            )
            return new_contact

    @staticmethod
    def create_contact(
        name: str,
        client_id: int,
        email: str = None,
        phone: str = None,
        position: str = None,
        notes: str = None,
        birth_date: str = None,
    ):

        if not Client.query.get(client_id):
            raise ValidationError("Cliente no encontrado.")

        contact = Contact(
            name=name,
            email=email,
            phone=phone,
            position=position,
            notes=notes,
            birth_date=birth_date,
            client_id=client_id,
        )

        db.session.add(contact)
        return contact

    def patch_obj(contact: Contact, data: dict):
        from .dto import ContactPatchDTO

        dto = ContactPatchDTO.model_validate(data)
        if dto.name is not None:
            contact.name = dto.name
        if dto.email is not None:
            contact.email = dto.email
        if dto.phone is not None:
            contact.phone = dto.phone
        if dto.position is not None:
            contact.position = dto.position
        if dto.notes is not None:
            contact.notes = dto.notes
        if dto.birth_date is not None:
            contact.birth_date = dto.birth_date

        try:
            db.session.add(contact)
            db.session.commit()
            return contact
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_obj(contact):
        db.session.delete(contact)
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
