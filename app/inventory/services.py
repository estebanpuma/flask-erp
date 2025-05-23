from flask import current_app, flash

from sqlalchemy.exc import SQLAlchemyError
from app import db

from .models import Warehouse, InventoryMovement, InventoryMovementType, InventoryMovementItem

from datetime import datetime


class MaterialGroupServices:

    @staticmethod
    def get_all_material_groups():
        from ..products.models import MaterialGroup
        material_groups = MaterialGroup.query.all()
        return material_groups
    
    @staticmethod
    def get_material_group(group_id):
        from ..products.models import MaterialGroup
        material_group = MaterialGroup.query.get_or_404(group_id)
        return material_group
    
    @staticmethod
    def create_material_group(code:str, name:str, description:str=None):
        from ..products.models import MaterialGroup
        new_material_group = MaterialGroup(code=code,
                                           name=name,
                                           description=description)
        try:
            db.session.add(new_material_group)
            db.session.commit()
            current_app.logger.info('MaterialGroup creado con exito')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error al crear material: {e}')
            raise ValueError('Ocurrió un error al crear el material')
            current_app.logger.warning(f'MaterialGroup no se pudo guardar. Error: {e}')
            raise ValueError('Ocurrio un error al guardar MaterialGroup')

    @staticmethod
    def update_material_group(group_id:int, code:str, name:str, description:str=None):
        from ..products.models import MaterialGroup
        group = MaterialGroup.query.get_or_404(group_id)
        
        group.code = code
        group.name = name
        group.description = description

        try:
            db.session.add(group)
            db.session.commit()
            current_app.logger.info('MaterialGroup actualizado con exito')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'MaterialGroup no se pudo guardar. Error: {e}')
            raise ValueError('Ocurrio un error al actualizar MaterialGroup')


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
    def create_material(code: str, name: str, unit: str, detail: str, price: float, group: int=None):
        """
        Create a new material.

        Parameters:
        code (str): The code of the material.
        group (int): The ID of the material group.
        name (str): The name of the material.
        unit (str): The unit of the material.
        detail (str): The detail description of the material.
        price (float): The price of the material.

            db.session.flush()
        Material: The newly created material.
        """
        from ..products import Material
        try:
            new_material = Material(code = code,
                                    material_group_id = group,
                                    name = name,
                                    detail = detail,
                                    unit = unit)
            from ..products.models import MaterialPriceHistory  
            
            
            db.session.add(new_material)
            db.session.flush()
            new_price = MaterialPriceHistory(material_id = new_material.id,
                                            price = price,
                                            start_date = datetime.today(),
                                            is_actual_price = True)
            db.session.add(new_price)
            db.session.commit()
            return new_material
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error al crear material: {e}')
            raise ValueError('Ocurrió un error al crear el material')


    @staticmethod
    def update_material(material_id:int, code:str, name:str, unit:str, detail:str, price:float, group:int=None):
        from ..products import Material
        material = Material.query.get_or_404(material_id)
        material.code = code,
        material.material_group_id = group,
        material.name = name,
        material.detail = detail,
        material.unit = unit
        
        from ..products.models import MaterialPriceHistory
        new_price = MaterialPriceHistory(material_id = material.id,
                                        price = price,
                                        start_date = datetime.today(),
                                        is_actual_price = True)
        
        try:
            db.session.add(material)
            db.session.add(new_price)
            db.session.commit()
            current_app.logger.info('Material guardado')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning('Error al actualizar material')
            raise ValueError(e)



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
                target_item = MaterialServices.get_material_by_code(item['code'])
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
                target_item = MaterialServices.get_material_by_code(item['code'])
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
            