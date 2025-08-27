from flask import current_app

from app import db

from ..core.exceptions import NotFoundError, ValidationError, AppError, ConflictError
from ..core.filters import apply_filters

from .models import Warehouse
from .dto import WarehouseCreateDTO, WarehouseUpdateDTO


class WarehouseService:

    @staticmethod
    def get_obj(id):
        warehouse = Warehouse.query.get(id)
        if not warehouse:
            raise NotFoundError(f'No existe bodega con ID: {id}')
        return warehouse
    

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(Warehouse, filters)
        

    @staticmethod
    def create_obj(data:dict)->Warehouse:
        with db.session.begin():
            dto = WarehouseCreateDTO(**data)
            warehouse = WarehouseService.create_warehouse(code=dto.code,
                                                          name=dto.name,
                                                          description=dto.description,
                                                          location=dto.location)
            return warehouse
        
    
    @staticmethod
    def create_warehouse(code:str, name:str, description:str=None, location:str=None):
        """Crea una nueva bodega"""
        warehouse = Warehouse(code=code,
                              name=name,
                              description=description,
                              location=location)
        db.session.add(warehouse)
        return warehouse
    
    @staticmethod
    def patch_obj(obj:Warehouse, data:dict)->Warehouse:
        dto = WarehouseUpdateDTO(**data)
        if dto.name is not None:
            obj.name = dto.name
        if dto.description is not None:
            obj.description = dto.description
        if dto.location is not None:
            obj.location = dto.location

        try:
            db.session.commit()
            return obj
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def delete_obj(obj:Warehouse)->bool:

        try:
            db.session.delete(obj)
            db.session.commit()
            return True
        except Exception as e:
            raise

    