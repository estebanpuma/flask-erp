# services/material_group_service.py
from app import db
from .models import MaterialGroup
from .dto.material_group_dto import MaterialGroupCreateDTO, MaterialGroupUpdateDTO
from ..core.exceptions import NotFoundError, ValidationError
from ..core.filters import apply_filters


class MaterialGroupService:

    @staticmethod
    def create_obj(data:dict):
        with db.session.begin():
            dto = MaterialGroupCreateDTO(**data)
            group = MaterialGroupService.create_group(dto)
            return group

    @staticmethod
    def create_group(dto: MaterialGroupCreateDTO) -> MaterialGroup:
        # Validar que no exista un grupo con el mismo nombre
        existing = db.session.query(MaterialGroup).filter_by(name=dto.name.strip()).first()
        if existing:
            raise ValidationError(f"Ya existe un grupo de materiales con el nombre: {dto.name}")

        group = MaterialGroup(
            code = dto.code.upper(),
            name=dto.name.strip(),
            description=dto.description
        )
        db.session.add(group)
        return group

    @staticmethod
    def get_obj(group_id: int) -> MaterialGroup:
        group = db.session.get(MaterialGroup, group_id)
        if not group:
            raise NotFoundError(f"Grupo de materiales con id {group_id} no encontrado.")
        return group

    @staticmethod
    def get_obj_list(filters: dict = None):
        return apply_filters(MaterialGroup, filters)

    @staticmethod
    def pacth_obj(group: MaterialGroup, data:dict) -> MaterialGroup:
        dto = MaterialGroupUpdateDTO(**data)
        if dto.name:
            # Validar que el nuevo nombre no esté en uso por otro grupo
            existing = db.session.query(MaterialGroup).filter(
                MaterialGroup.name == dto.name.strip(),
                MaterialGroup.id != group.id
            ).first()
            if existing:
                raise ValidationError(f"Ya existe un grupo de materiales con el nombre: {dto.name}")

            group.name = dto.name.strip()

        if dto.description is not None:
            group.description = dto.description
        try:
            db.session.commit()
            return group
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def delete_obj(group:MaterialGroup):
        try:
            db.session.delete(group)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise
