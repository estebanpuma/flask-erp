from flask import current_app

from sqlalchemy.exc import SQLAlchemyError
from app import db

from .models import Warehouse, InventoryMovement, InventoryMovementType, InventoryMovementItem

from datetime import datetime

class MaterialServices:

    @staticmethod
    def search_material(query):
        from ..products.models import Material
    
        if '<by_code>' in query:
            code = query.removeprefix('<by_code>').upper()           
            result = Material.query.filter_by(code = code).first()                    
            return list({result})
        

        results_by_code = Material.query.filter(Material.code.ilike(f'%{query}%')).all()
        results_by_name = Material.query.filter(Material.name.ilike(f'%{query}%')).all()

        results = list({material.id: material for material in results_by_name + results_by_code}.values())
        return results

    @staticmethod
    def get_material(material_id):
        from ..products.models import Material
        material = Material.query.get_or_404(material_id)
        return material
    
    @staticmethod
    def get_material_by_code(material_code):
        current_app.logger.warning(f'Este warning: {material_code}')
        code = material_code.upper()
        from ..products.models import Material
        result = Material.query.filter_by(code = code).first()
        return result
    
    @staticmethod
    def get_all_materials():
        from ..products import Material
        materials = Material.query.all()
        return materials

    @staticmethod
    def create_material(code, name, unit, description=None):
        from ..products import Material
        new_material = Material(code = code,
                                name = name,
                                description = description,
                                unit = unit)
        
        try:
            db.session.add(new_material)
            db.session.commit()
            return new_material
        except Exception as e:
            db.session.rollback()



class WarehouseServices:

    @staticmethod
    def get_warehouse(warehouse_id):
        
        warehouse = Warehouse.query.get_or_404(warehouse_id)
        return warehouse
    
    @staticmethod
    def get_all_warehouses():
       
        warehouses = Warehouse.query.all()
        return warehouses

    @staticmethod
    def create_warehouse(code, name, location, description=None):
        
        new_warehouse = Warehouse(code = code,
                                name = name,
                                description = description,
                                location = location)
        
        try:
            db.session.add(new_warehouse)
            db.session.commit()
            return new_warehouse
        except Exception as e:
            db.session.rollback()
        

class InventoryService:

    @staticmethod
    def get_item_movements(item_type, code):

        movements = []
        items = InventoryMovementItem.query.filter_by(item_code = code).all()
        for item in items:
            if item.movement.item_type == item_type:
                movements.append(item)
        return movements
    
    

    @staticmethod
    def create_inventory_movement( 
                                    movement_trigger: str,
                                    item_type: str, 
                                    movement_type: str, 
                                    date, 
                                    responsible: int, 
                                    warehouse: int, 
                                    items, 
                                    document=None):
        
        from ..products.models import Material,Product

        #creo un diccionario que traduce de tipo de elemento a modelos
        item_type_models = {
            'RAWMATERIAL': Material,
            'PRODUCT': Product,
            
        }
        obj=None
        if item_type in item_type_models:
            obj = item_type_models[item_type]
        else:
            raise ValueError('item_type incorrecto')
        
        try:
            # Crear la instancia de movimiento de inventario
            new_entry = InventoryMovement(
                date=date,
                responsible_id=responsible,
                warehouse_id=warehouse,
                movement_type=movement_type,
                movement_trigger = movement_trigger,
                item_type=item_type,
                document=document
            )
            
            # Agregar movimiento de inventario a la sesión
            db.session.add(new_entry)
            db.session.flush()  # Ejecuta el SQL para obtener el ID de `new_entry`
            
            #llamo a material para obtener el stock a la fecha del movimiento 
            
            item_obj = obj.query.filter_by(code = item.code).first()
            item_stock = item_obj.stock
            # Crear entradas de inventario
            for item in items:
                new_item = InventoryMovementItem(
                    inventory_movement_id=new_entry.id,
                    item_id=item.id,
                    code=item.code,
                    qty=item.qty,
                    stock = item_stock + item.qty if item_stock else item.qty
                )
                db.session.add(new_item)
            
            # Guardar los cambios en la base de datos
            db.session.commit()
            
            return new_entry

        except SQLAlchemyError as e:
            db.session.rollback()
            # Loggeo del error
            current_app.logger.warning(f'Error al crear el movimiento de inventario: {str(e)}') 
            return None
        
            
    @staticmethod
    def create_material_entry(movement_trigger, date, responsible, warehouse, items, document=None):
        item_type = 'RAWMATERIAL'
        movement_type = 'ENTRY'
        movement_trigger = 'PURCHASE'
        try:
            valid_items = []
            for item in items:
                target_item = MaterialServices.get_material_by_code(item.code)
                if target_item:
                    valid_items.append(target_item)
                    
                
                else:
                    raise Exception('No item match')
                
            new_entry = InventoryService.create_inventory_movement(item_type=item_type,
                                                                    movement_trigger = movement_trigger,
                                                                    movement_type=movement_type,
                                                                    date=date,
                                                                    responsible=responsible,
                                                                    warehouse = warehouse,
                                                                    items=valid_items,
                                                                    document=document
                                                                    )
            return new_entry
                
        except Exception as e:
            current_app.logger.warning(f'Error:{e}')
            return None
