# services/supplier_service.py
from app import db
from .models import Supplier
from .dto import SupplierCreateDTO, SupplierUpdateDTO
from ..core.exceptions import NotFoundError, ValidationError


class SupplierService:
    @staticmethod
    def create_obj(data:dict)->Supplier:
        with db.session.begin():
            dto = SupplierCreateDTO(**data)
            supplier = SupplierService.create(dto)
            return supplier

    @staticmethod
    def create(dto: SupplierCreateDTO) -> Supplier:
        supplier = Supplier.query.filter(Supplier.ruc_or_ci==dto.ruc_or_ci).first()
        if supplier:
            raise ValidationError(f'Ya existe un proveedor registrado con el RUC:{str(dto.ruc_or_ci)}')
        supplier = Supplier(
            name=dto.name,
            ruc_or_ci=dto.ruc_or_ci,
            phone=dto.phone,
            email=dto.email,
            address=dto.address
        )
        db.session.add(supplier)
        return supplier

    @staticmethod
    def get_obj(supplier_id: int) -> Supplier:
        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            raise NotFoundError(f"Supplier con id {supplier_id} no encontrado.")
        return supplier

    @staticmethod
    def get_obj_list(filters: dict = None):
        query = db.session.query(Supplier)
        if filters:
            if 'name' in filters:
                query = query.filter(Supplier.name.ilike(f"%{filters['name']}%"))
            if 'ruc_or_ci' in filters:
                query = query.filter(Supplier.ruc_or_ci == filters['ruc_or_ci'])
        return query.all()


    @staticmethod
    def patch_obj(supplier:Supplier, data:dict) -> Supplier:
        dto = SupplierUpdateDTO(**data)
        if dto.name is not None:
            supplier.name = dto.name.strip()
        if dto.ruc_or_ci is not None:
            supplier.ruc_or_ci = dto.ruc_or_ci.strip()
        if dto.phone is not None:
            supplier.phone = dto.phone.strip()
        if dto.email is not None:
            supplier.email = dto.email.strip()
        if dto.address is not None:
            supplier.address = dto.address.strip()
        try:
            db.session.commit()
            return supplier
        except Exception as e:
            db.session.rollback()
            raise


