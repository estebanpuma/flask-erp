# services/supplier_service.py
from app import db

from ..core.exceptions import ConflictError, NotFoundError
from ..core.filters import apply_filters
from .dto import SupplierCreateDTO, SupplierUpdateDTO
from .models import Supplier, SupplierContact


class SupplierService:
    @staticmethod
    def create_obj(data: dict) -> Supplier:
        with db.session.begin():
            dto = SupplierCreateDTO(**data)
            supplier = SupplierService.create_supplier(
                name=dto.name,
                ruc_or_ci=dto.ruc_or_ci,
                phone=dto.phone,
                email=dto.email,
                address=dto.address,
            )
            return supplier

    @staticmethod
    def create_supplier(
        name: str,
        ruc_or_ci: str,
        phone: str = None,
        email: str = None,
        address: str = None,
    ) -> Supplier:

        supplier = Supplier.query.filter(Supplier.ruc_or_ci == ruc_or_ci).first()
        if supplier:
            raise ConflictError(
                f"Ya existe un proveedor registrado con el RUC:{str(ruc_or_ci)}"
            )
        supplier = Supplier(name=name, ruc_or_ci=ruc_or_ci, address=address)
        db.session.add(supplier)
        db.session.flush()
        SupplierContactService.create_contact(
            supplier_id=supplier.id,
            name=name,
            email=email,
            phone=phone,
            is_primary=True,
        )

        return supplier

    @staticmethod
    def get_obj(supplier_id: int) -> Supplier:
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            raise NotFoundError(f"Supplier con id {supplier_id} no encontrado.")
        return supplier

    @staticmethod
    def get_obj_list(filters: dict = None):

        return apply_filters(Supplier, filters)

    @staticmethod
    def patch_obj(supplier: Supplier, data: dict) -> Supplier:
        dto = SupplierUpdateDTO(**data)
        if dto.name is not None:
            supplier.name = dto.name.strip()
        if dto.ruc_or_ci is not None:
            supplier.ruc_or_ci = dto.ruc_or_ci.strip()

        if dto.address is not None:
            supplier.address = dto.address.strip()

        if dto.lifecycle_status is not None:
            supplier.lifecycle_status = dto.lifecycle_status.strip()

        db.session.add(supplier)
        try:
            db.session.commit()
            return supplier
        except Exception:
            db.session.rollback()
            raise


class SupplierContactService:
    @staticmethod
    def create_obj(data: dict) -> SupplierContact:
        with db.session.begin():
            from .dto import SupplierContactCreateDTO

            dto = SupplierContactCreateDTO(**data)
            obj = SupplierContactService.create_contact(
                supplier_id=dto.supplier_id,
                name=dto.name,
                position=dto.position,
                email=dto.email,
                phone=dto.phone,
                is_primary=dto.is_primary,
            )
            return obj

    @staticmethod
    def create_contact(
        supplier_id: int,
        name: str,
        position: str = None,
        email: str = None,
        phone: str = None,
        is_primary: bool = False,
    ) -> SupplierContact:

        contact = SupplierContact(
            supplier_id=supplier_id,
            name=name,
            position=position,
            email=email,
            phone=phone,
            is_primary=is_primary,
        )
        db.session.add(contact)
        return contact

    @staticmethod
    def get_obj(id: int) -> SupplierContact:
        contact = db.session.get(SupplierContact, id)
        if not contact:
            raise NotFoundError(f"Contacto de proveedor con id {id} no encontrado.")
        return contact

    @staticmethod
    def get_obj_list(filters: dict = None) -> list[SupplierContact]:
        return apply_filters(SupplierContact, filters)

    @staticmethod
    def get_obj_list_by_client(client_id: int) -> list[SupplierContact]:
        return db.session.query(SupplierContact).filter_by(client_id=client_id).all()

    @staticmethod
    def patch_obj(
        instance: SupplierContact,
        data: dict,
    ) -> SupplierContact:
        from .dto import SupplierContactUpdateDTO

        dto = SupplierContactUpdateDTO(**data)

        if dto.name is not None:
            instance.name = dto.name.strip()
        if dto.position is not None:
            instance.position = dto.position.strip()
        if dto.email is not None:
            instance.email = dto.email.strip()
        if dto.phone is not None:
            instance.phone = dto.phone.strip()
        if dto.is_primary is not None:
            instance.is_primary = dto.is_primary
        db.session.add(instance)
        db.session.commit()
        return instance

    @staticmethod
    def delete_obj(contact: SupplierContact):
        try:
            db.session.delete(contact)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
