from flask import current_app, flash

from sqlalchemy.exc import SQLAlchemyError
from app import db

from .models import Warehouse, InventoryMovement, InventoryMovementType, InventoryMovementItem

from datetime import datetime





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
    def get_item_movementsNew(item_type, item_code):
        items = InventoryMovementItem.query.join(InventoryMovement).filter(InventoryMovementItem.item_code == item_code.upper()).order_by(InventoryMovement.date.asc()).all()
        movements = []
        print(f'items ahimimso: {items}')
        entries = 0
        exits = 0
        for item in items:
            if item.movement.item_type == item_type:
                type = None
                if item.movement.movement_type.value == 'Ingreso':
                    entries = entries + item.qty
                    type = 'Ingreso'
                if item.movement.movement_type.value == 'Egreso':
                    exits = exits + item.qty
                    type = 'Egreso'
                nstock = entries - exits
                nitem = {
                    'id': item.id,
                    'item_id': item.item_id,
                    'item_code': item.item_code,
                    'inventory_movement_id': item.inventory_movement_id,
                    'date': item.movement.date,
                    'movement_type': type,
                    'document_number': item.movement.document_number,
                    'movement_trigger': item.movement.movement_trigger.value,
                    'qty': item.qty,
                    'stock': nstock
                }
                movements.append(nitem)
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
        
        from ..products.models import Product
        from ..materials.models import Material

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
        
        
        # Crear la instancia de movimiento de inventario
        new_movement = InventoryMovement(
            date=date,
            responsible_id=responsible,
            warehouse_id=warehouse,
            movement_type=movement_type,
            movement_trigger = movement_trigger,
            item_type=item_type,
            document_number=document
        )
        try:  
            # Agregar movimiento de inventario a la sesión
            db.session.add(new_movement)
            db.session.flush()  # Ejecuta el SQL para obtener el ID de `new_entry`
            current_app.logger.info('Nuevo movimiento de inventario anadido a sesion')
            # Crear entradas de inventario
            for item in items:
                item_code = str(item['code']).upper()
                item_obj = obj.query.filter_by(code = item_code).first()

                if item_obj is None:
                    current_app.logger.warning(f'No se encontró el item: {item['code']}')
                    raise ValueError(f'No se encontró el item: {item['code']}')
                
                item_stock = item_obj.stock or 0
                qty = int(item['qty'])
                if movement_type == 'EXIT':
                    qty = int(item['qty'])*(-1)

                new_item = InventoryMovementItem(
                    inventory_movement_id=new_movement.id,
                    item_id=item_obj.id,
                    item_code=str(item['code']).upper(),
                    qty=qty,
                    stock = item_stock + qty
                )
                db.session.add(new_item)
                
                item_obj.stock = item_stock + qty
                # Guardar los cambios en la base de datos
            db.session.commit()
            current_app.logger.info(f'Nuevo movimiento de inventario guardado id={new_movement.id}')
            return new_movement

        except SQLAlchemyError as e:
            db.session.rollback()
            # Loggeo del error
            current_app.logger.warning(f'Error SQL al crear el movimiento de inventario: {str(e)}') 
            return None
        except Exception as e:
            db.session.rollback()
            # Loggeo del error
            current_app.logger.warning(f'Error al crear el movimiento de inventario: {str(e)}')
            return None
            
    @staticmethod
    def create_material_entry(movement_trigger, date, responsible, warehouse, items, document=None):
        item_type = 'RAWMATERIAL'
        movement_type = 'ENTRY'
        movement_trigger = movement_trigger
        try:
            valid_items = []
            for item in items:
                target_item = None
                if target_item:
                    valid_items.append(item)
                    
                
                else:
                    raise ValueError('No item match')
  
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
            current_app.logger.warning(f'Error al crear entrada de material:{e}')
            return None

    @staticmethod
    def create_material_exit(movement_trigger,
                             date,
                             responsible,
                             warehouse,
                             items,
                             document=None):
        
        item_type = "RAWMATERIAL"

        movement_type = 'EXIT'

        movement_trigger = movement_trigger

        try:
            valid_items = []
            for item in items:
                target_item = None
                if target_item:
                    valid_items.append(item)
                else:
                    raise ValueError(f'Codigo: {item['code']}, no perteneca ningun item')
            
            new_exit = InventoryService.create_inventory_movement(movement_trigger=movement_trigger,
                                                                  item_type=item_type,
                                                                  movement_type=movement_type,
                                                                  date=date,
                                                                  responsible=responsible,
                                                                  warehouse=warehouse,
                                                                  items=valid_items,
                                                                  document=document)

            return new_exit

        except Exception as e:
            current_app.logger.warning(f'Error al crear egreso de material:{e}')
            