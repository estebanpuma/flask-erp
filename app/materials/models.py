from app import db

from datetime import datetime

from ..common.models import BaseModel


class MaterialGroup(BaseModel):
    __tablename__ = 'material_groups'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=True, unique=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(), nullable=True)

    materials = db.relationship('Material', back_populates='group', lazy='dynamic')

    def __repr__(self):
        return f"<MaterialGroup {self.name}>"


class Material(BaseModel):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)  # Ej: Cuero, Sintético, Textil
    detail = db.Column(db.String(), nullable=True)
    unit = db.Column(db.String(10), nullable=False)

    group_id = db.Column(db.Integer, db.ForeignKey('material_groups.id'), nullable=True)
    group = db.relationship('MaterialGroup', back_populates='materials')

    product_material_details = db.relationship('ProductVariantMaterialDetail', back_populates='material')
    # Relación con lotes
    lots = db.relationship('MaterialLot', back_populates='material', cascade='all, delete-orphan', lazy='dynamic')


    def __repr__(self):
        return f'<Material(name={self.name})>'
    

class MaterialLot(BaseModel):
    __tablename__ = 'material_lots'

    id = db.Column(db.Integer, primary_key=True)
    lot_number = db.Column(db.String(50))  # Ej: LOTE-2025-001
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
   
    quantity_committed = db.Column(db.Float, default=0) # Stock comprometido para órdenes de producción
    quantity = db.Column(db.Float, nullable=False)# Stock físico disponible
    unit_cost = db.Column(db.Float, nullable=False)
    received_date = db.Column(db.Date, nullable=False, default=datetime.today())

   
    # Relaciones
    material = db.relationship('Material', back_populates='lots')
    supplier = db.relationship('Supplier', back_populates='material_lots')
    warehouse = db.relationship('Warehouse', back_populates='lots')
    movements = db.relationship('InventoryMovement', back_populates='lot', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f"<MaterialLot {self.lot_number} - {self.material.code} - {self.warehouse.name}>"


class InventoryMovement(BaseModel):
    __tablename__ = 'inventory_movements'

    id = db.Column(db.Integer, primary_key=True)
    movement_type = db.Column(db.String(20), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('material_lots.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.today())
    note = db.Column(db.String(255))

    lot = db.relationship('MaterialLot', back_populates='movements')

    def __repr__(self):
        return f"<InventoryMovement {self.movement_type} - {self.quantity} ({self.lot.material.code})>"


class Supplier(BaseModel):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ruc_or_ci = db.Column(db.String(20), unique=True, nullable=False)
    contact_info = db.Column(db.String(255))
    material_lots = db.relationship('MaterialLot', back_populates='supplier', lazy='dynamic')

    def __repr__(self):
        return f"<Supplier {self.name}>"