# services/material_service.py
from flask import current_app
from app import db
from .models import Material, MaterialGroup, MaterialStock, MaterialLot
from .dto.material_dto import MaterialCreateDTO, MaterialUpdateDTO
from ..core.exceptions import NotFoundError, ValidationError
from ..core.filters import apply_filters

class MaterialService:

    @staticmethod
    def search_material(query:str, limit=15):
        q = query.strip().lower()
        clients = (
            db.session.query(
            Material.id,
            Material.code,
            Material.name,
            Material.unit,
            Material.detail,
            )
            .filter(
                (Material.code.ilike(f'%{q}%')) |
                (Material.name.ilike(f'%{q}%')) 
            )
            .order_by(Material.name.asc())
            .limit(limit)
            .all()
        )
        return clients

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
            detail=dto.detail,
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
    def patch_obj(material:Material, data:dict) -> Material:

        dto = MaterialUpdateDTO(**data)
        
        if dto.name:
            material.name = dto.name.strip()
        if dto.detail is not None:
            material.detail = dto.detail
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
            current_app.logger.warning('No se puedo actualizar el material.')
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


class MaterialStockService:

    @staticmethod
    def update_stock(material_id: int, warehouse_id: int):
        """
        Actualiza el stock consolidado de un material en una bodega:
        - quantity_physical: suma de cantidades físicas reales en todos los lotes
        - quantity_available: quantity_physical - sum(quantity_committed en lotes)
        """

        # Sumar cantidad física real en todos los lotes
        physical_quantity = db.session.query(
            db.func.coalesce(db.func.sum(MaterialLot.quantity), 0.0)
        ).filter(
            MaterialLot.material_id == material_id,
            MaterialLot.warehouse_id == warehouse_id
        ).scalar()

        # Sumar reservas (quantity_committed) de todos los lotes
        reserved_quantity = db.session.query(
            db.func.coalesce(db.func.sum(MaterialLot.quantity_committed), 0.0)
        ).filter(
            MaterialLot.material_id == material_id,
            MaterialLot.warehouse_id == warehouse_id
        ).scalar()

        # Calcular cantidad disponible
        available_quantity = physical_quantity - reserved_quantity

        # Obtener o crear el registro de stock consolidado
        stock = db.session.query(MaterialStock).filter_by(
            material_id=material_id,
            warehouse_id=warehouse_id
        ).first()

        if not stock:
            stock = MaterialStock(
                material_id=material_id,
                warehouse_id=warehouse_id
            )
            db.session.add(stock)

        # Actualizar cantidades
        stock.quantity = physical_quantity
        stock.quantity_available = available_quantity

        # No hacemos commit aquí ➜ lo hace el servicio padre
        return stock
    

    @staticmethod
    def get_total_stock(material_id: int) -> float:
        # Sumar la cantidad total de todas las bodegas para este material
        total_stock = (
            db.session.query(db.func.sum(MaterialStock.quantity))
            .filter_by(material_id=material_id)
            .scalar()
        ) or 0.0


        return total_stock
    

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(MaterialStock, filters)


    @staticmethod
    def get_warehouse_stock(warehouse_id:int, material_id:int)->MaterialStock:
        from ..inventory.models import Warehouse
        warehouse = Warehouse.query.get(warehouse_id)
        if not warehouse:
            raise ValidationError('No existe una bodega con el id seleccionado')
        material = Material.query.get(material_id)
        if not material:
            raise ValidationError('No existe un material con el id seleccionado')
        
        stock = MaterialStock.query.filter(MaterialStock.material_id==material_id, 
                                           MaterialStock.warehouse_id==warehouse_id).all()
        
        return stock
    
    @staticmethod
    def get_total_stocks_by_material():
        materials = MaterialService.get_obj_list()
        materials_stock = []
        for material in materials:
            stock = MaterialStockService.get_total_stock(material.id)
            m_stock = {'id': material.id,
                       'code': material.code,
                       'name': material.name,
                       'stock': stock
                       }
            materials_stock.append(m_stock)

        return materials_stock