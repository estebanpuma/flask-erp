# services/material_service.py
from flask import current_app
from app import db
from .models import Material, MaterialGroup
from .dto.material_dto import MaterialCreateDTO, MaterialUpdateDTO
from ..core.exceptions import NotFoundError, ValidationError
from ..core.filters import apply_filters

class MaterialService:

    @staticmethod
    def create_obj(data:dict):
        with db.session.begin():
            dto = MaterialCreateDTO(**data)
            material = MaterialService.create_material(dto)
            return material

    @staticmethod
    def create_material(dto: MaterialCreateDTO) -> Material:
        # Verificar si el código ya existe
        existing = db.session.query(Material).filter_by(code=dto.code).first()
        if existing:
            raise ValidationError(f"El material con código {dto.code} ya existe.")

        material = Material(
            code=dto.code.strip().upper(),
            name=dto.name.strip(),
            description=dto.description,
            unit=dto.unit,
            group_id=dto.group_id
        )
        db.session.add(material)
        return material

    @staticmethod
    def get_obj(material_id: int) -> Material:
        material = db.session.get(Material, material_id)
        if not material:
            raise NotFoundError(f"Material con id {material_id} no encontrado.")
        return material

    @staticmethod
    def get_obj_list(filters: dict = None):
        query = db.session.query(Material)
        if filters:
            if 'group_id' in filters:
                query = query.filter(Material.group_id == filters['group_id'])
                return query.all()
            if 'name' in filters:
                query = query.filter(Material.name.ilike(f"%{filters['name']}%"))
                return query.all()
        return apply_filters(Material, filters)
        

    @staticmethod
    def patch_obj(material:Material, dto: MaterialUpdateDTO) -> Material:
        

        if dto.name:
            material.name = dto.name.strip()
        if dto.description is not None:
            material.description = dto.description
        if dto.unit is not None:
            material.unit = dto.unit
        if dto.group_id is not None:
            material.group_id = dto.group_id

        try:
            db.session.commit()
            # Nota: No se permite editar el código por trazabilidad
            return material
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning('No se puedo actualizar el material')
            raise

    @staticmethod
    def delete_obj(material:Material):
        from ..products.models import ProductVariantMaterialDetail
        # Validar que no esté en uso en la producción
        #used_in_production = db.session.query(ProductionMaterialUsage).filter_by(material_id=material_id).first()
        #if used_in_production:
        #    raise ValidationError("No se puede eliminar un material que ya ha sido utilizado en producción.")

        # Validar que no está en uso en ProductVariantMaterialDetail
        in_use_in_variant = db.session.query(ProductVariantMaterialDetail).filter_by(material_id=material.id).first()
        if in_use_in_variant:
            raise ValidationError("No se puede eliminar un material que está definido en variantes de producto.")
    
        
        try:
            db.session.delete(material)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning("No se pudo eliminar el material")