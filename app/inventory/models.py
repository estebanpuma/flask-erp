from app import db

from app.common.models import BaseModel, SoftDeleteMixin

from enum import Enum



class ItemInventory(Enum):
    RAWMATERIAL = 'Materia prima'
    PRODUCT = 'Producto'
    WIP = 'Producto en proceso'
    TOOLS = 'Herramientas'

class InventoryMovementType(Enum):
    ENTRY = 'Ingreso'
    EXIT = 'Egreso'
    

class InventoryMovementTrigger(Enum):
    SALES = 'VENTAS'
    PURCHASE = 'COMPRA'
    PRODUCTION = 'PRODUCCION'
    ROTATION = 'ROTACION'
    REMOVE = 'BAJA'
    ADJUST = 'AJUSTE'



    

class Warehouse(BaseModel, SoftDeleteMixin):
    __tablename__ = 'warehouses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(), nullable=True)
    location = db.Column(db.String(), nullable=True)

    inventory_movements = db.relationship('InventoryMovement', back_populates='warehouse', cascade='all, delete-orphan')
    

class InventoryMovement(BaseModel):
    __tablename__ = 'inventory_movements'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    movement_type = db.Column(db.Enum(InventoryMovementType), nullable=False)
    item_type = db.Column(db.String(), nullable=False)
    movement_trigger = db.Column(db.Enum(InventoryMovementTrigger), nullable=False)
    document_number = db.Column(db.String())
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    warehouse = db.relationship('Warehouse', back_populates='inventory_movements')
    items = db.relationship('InventoryMovementItem', back_populates='movement', cascade='all, delete-orphan')


class InventoryMovementItem(BaseModel):

    __tablename__ = 'inventory_movement_items'

    id = db.Column(db.Integer, primary_key=True)
    inventory_movement_id = db.Column(db.Integer, db.ForeignKey('inventory_movements.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    item_code = db.Column(db.String())
    qty = qty = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Float, nullable=True, default=0)
    
    movement = db.relationship('InventoryMovement', back_populates='items')

