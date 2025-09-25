from flask import current_app

from app import db

from ..common.utils import ExcelImportService
from ..core.exceptions import ConflictError, NotFoundError, ValidationError
from .models import Material, MaterialGroup


class MaterialGroupServices:

    @staticmethod
    def get_list(filters=None):
        query = MaterialGroup.query

        if filters:
            if "code" in filters:
                query = query.filter(MaterialGroup.code == str(filters["code"]).upper())
            if "name" in filters:
                query = query.filter(MaterialGroup.name == str(filters["name"]))

        return query.all()

    @staticmethod
    def get_material_group(group_id):
        material_group = MaterialGroup.query.get(group_id)
        if not material_group:
            raise NotFoundError("Grupo no encontrado")
        return material_group

    @staticmethod
    def create_material_group(code: str, name: str, description: str = None):

        existing = MaterialGroup.query.filter_by(code=code.strip().upper()).first()
        if existing:
            raise ConflictError("Ya existe un grupo con ese código.")
        new_material_group = MaterialGroup(
            code=code, name=name, description=description
        )
        try:
            db.session.add(new_material_group)
            db.session.commit()
            current_app.logger.info("MaterialGroup creado con exito")
            return new_material_group
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f"MaterialGroup no se pudo guardar. Error: {e}")
            raise

    @staticmethod
    def update(instance, data):

        if "name" in data:
            name = data["name"].strip()
            existing = MaterialGroup.query.filter_by(
                name=name, code=instance.code
            ).first()
            if existing and instance:
                raise ConflictError(
                    "Ya existe un grupo con ese nombre para el codigo seleccionado."
                )

        if "code" in data:
            code = data["code"].strip()
            existing = MaterialGroup.query.filter_by(code=code).first()
            if existing and instance:
                raise ConflictError("Ya existe un grupo con ese codigo.")

        for field in ["code", "name", "description"]:
            if field in data:
                setattr(instance, field, data[field])

        try:
            db.session.commit()
            return instance
        except:
            db.session.rollback()
            raise

    @staticmethod
    def delete(id):
        material_group = MaterialGroup.query.get(id)
        if not material_group:
            raise NotFoundError("Grupo no encontrado")
        db.session.delete(material_group)
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            raise


class MaterialServices:

    @staticmethod
    def get(material_id):
        material = Material.query.get(material_id)
        if not material:
            raise NotFoundError("Material no encontrado")
        return material

    @staticmethod
    def get_list(filters=None):
        query = Material.query
        if filters:
            if "code" in filters:
                query = query.filter(Material.code == str(filters["code"]))
            if "material_group_id" in filters:
                query = query.filter(
                    Material.material_group_id == int(filters["material_group_id"])
                )

        return query.all()

    @staticmethod
    def create(data):
        existing = Material.query.filter_by(code=data["code"].strip().upper()).first()
        if existing:
            raise ConflictError("Ya existe un material con ese código.")

        material = Material(
            code=data["code"].strip().upper(),
            name=data["name"].strip(),
            detail=data.get("detail"),
            unit=data["unit"],
            group_id=data.get("material_group_id"),
        )

        db.session.add(material)
        try:
            db.session.commit()
            return material

        except:
            db.session.rollback()
            current_app.logger.warning("No se pudo crear el material")
            raise

    @staticmethod
    def update(instance, data):
        for field in ["code", "name", "detail", "unit", "stock", "material_group_id"]:
            if field in data:
                setattr(instance, field, data[field])
        db.session.commit()
        return instance

    @staticmethod
    def delete(material_id):
        material = Material.query.get(material_id)
        if not material:
            raise NotFoundError("Material no encontrado")
        db.session.delete(material)
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            current_app.logger.warning("No se pudo borrar el material")
            raise

    @staticmethod
    def create_from_excel_row(data):
        if Material.query.filter_by(code=data["code"]).first():
            raise ValidationError(f"Ya existe material con código: {data['code']}")

        material = Material(
            code=data["code"],
            name=data["name"],
            unit=data["unit"],
            detail=data.get("detail"),
        )
        db.session.add(material)
        # No commit aquí → el recurso o caller decide cuándo hacer commit
        return material


class MaterialExcelImportService(ExcelImportService):
    required_columns = ["code", "name", "unit"]

    @staticmethod
    def handle_row(data):
        return MaterialServices.create_from_excel_row(data)
