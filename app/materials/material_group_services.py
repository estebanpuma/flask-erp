# services/material_group_service.py
from app import db

from ..core.exceptions import NotFoundError, ValidationError
from ..core.filters import apply_filters
from .dto.material_group_dto import (
    MaterialGroupCreateDTO,
    MaterialGroupUpdateDTO,
    MaterialSubGroupCreateDTO,
    MaterialSubGroupUpdateDTO,
)
from .models import MaterialGroup, MaterialSubGroup


class MaterialGroupService:

    @staticmethod
    def create_obj(data: dict):
        """Crea un nuevo grupo de materiales[MaterialGroup] a partir de un dict y lo valida con DTO"""
        with db.session.begin():
            dto = MaterialGroupCreateDTO(**data)
            group = MaterialGroupService.create_group(dto)
            return group

    @staticmethod
    def create_group(dto: MaterialGroupCreateDTO) -> MaterialGroup:
        """Crea un nuevo grupo de materiales[MaterialGroup] a partir de datos validados"""
        existing = (
            db.session.query(MaterialGroup).filter_by(name=dto.name.strip()).first()
        )
        if existing:
            raise ValidationError(
                f"Ya existe un grupo de materiales con el nombre: {dto.name}"
            )

        group = MaterialGroup(
            code=dto.code.upper(),
            name=dto.name.strip(),
            description=dto.description,
        )
        db.session.add(group)
        return group

    @staticmethod
    def get_obj(group_id: int) -> MaterialGroup:
        """Devuelve un grupo de materiales[MaterialGroup] según su id."""
        group = db.session.get(MaterialGroup, group_id)
        if not group:
            raise NotFoundError(f"Grupo de materiales con id {group_id} no encontrado.")
        return group

    @staticmethod
    def get_obj_list(filters: dict = None):
        """Devuelve una lista de grupos de materiales[MaterialGroup] según los filtros."""
        return apply_filters(MaterialGroup, filters)

    @staticmethod
    def pacth_obj(group: MaterialGroup, data: dict) -> MaterialGroup:
        """Edita un grupo de materiales[MaterialGroup]"""
        dto = MaterialGroupUpdateDTO(**data)
        if dto.name:
            # Validar que el nuevo nombre no esté en uso por otro grupo
            existing = (
                db.session.query(MaterialGroup)
                .filter(
                    MaterialGroup.name == dto.name.strip(), MaterialGroup.id != group.id
                )
                .first()
            )
            if existing:
                raise ValidationError(
                    f"Ya existe un grupo de materiales con el nombre: {dto.name}"
                )

            group.name = dto.name.strip()

        if dto.description is not None:
            group.description = dto.description
        try:
            db.session.commit()
            return group
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_obj(group: MaterialGroup):
        """Elimina un grupo de materiales[MaterialGroup]"""
        try:
            db.session.delete(group)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise


class MaterialSubGroupService:
    @staticmethod
    def get_obj(id: int) -> MaterialSubGroup:
        """Devuelve un subgrupo de materiales[MaterialSubGroup] según su id."""
        subgroup = MaterialSubGroup.query.get(id)
        if not subgroup:
            raise NotFoundError(f"Subgrupo de materiales con id {id} no encontrado.")
        return subgroup

    @staticmethod
    def get_obj_list(filters: dict = None) -> list[MaterialSubGroup]:
        """Devuelve una lista de subgrupos de materiales[MaterialSubGroup] según los filtros."""
        return apply_filters(MaterialSubGroup, filters)

    @staticmethod
    def create_obj(data: dict) -> MaterialSubGroup:
        """Crea un nuevo subgrupo de materiales[MaterialSubGroup] a partir de un dict y lo valida con DTO"""
        with db.session.begin():
            dto = MaterialSubGroupCreateDTO(**data)
            subgroup = MaterialSubGroupService.create_subgroup(
                name=dto.name,
                description=dto.description,
                group_id=dto.material_group_id,
            )
            return subgroup

    @staticmethod
    def create_subgroup(
        name: str, description: str = None, group_id: int = None
    ) -> MaterialSubGroup:
        """Crea un nuevo subgrupo de materiales[MaterialSubGroup] a partir de datos validados"""
        new_subgroup = MaterialSubGroup(
            name=name, description=description, group_id=group_id
        )
        db.session.add(new_subgroup)
        return new_subgroup

    @staticmethod
    def patch_obj(subgroup: MaterialSubGroup, data: dict) -> MaterialSubGroup:
        """Edita un Subgrupo de materiales[MaterialSubGroup]"""
        dto = MaterialSubGroupUpdateDTO(**data)
        if dto.name:
            subgroup.name = dto.name
        if dto.description is not None:
            subgroup.description = dto.description
        if dto.group_id is not None:
            subgroup.group_id = dto.group_id
        db.session.add(subgroup)
        print(subgroup.group_id)
        print(subgroup.group.name)
        try:
            db.session.commit()
            return subgroup
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_obj(subgroup: MaterialSubGroup):
        """Elimina un Subgrupo de materiales[MaterialSubGroup]"""
        try:
            db.session.delete(subgroup)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
