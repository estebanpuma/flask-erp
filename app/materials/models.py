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
    material_stocks = db.relationship('MaterialStock', back_populates='material')


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
    note = db.Column(db.String(), nullable=True)

   
    # Relaciones
    material = db.relationship('Material', back_populates='lots')
    supplier = db.relationship('Supplier', back_populates='material_lots')
    warehouse = db.relationship('Warehouse', back_populates='lots')
    movements = db.relationship('InventoryMovement', back_populates='lot', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f"<MaterialLot {self.lot_number} - {self.material.code} - {self.warehouse.name}>"
    


class MaterialStock(db.Model):
    __tablename__ = 'material_stocks'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    quantity_available = db.Column(db.Float, default=0.0)

    __table_args__ = (
        db.UniqueConstraint('material_id', 'warehouse_id', name='uq_material_stock_warehouse'),
    )

    material = db.relationship('Material', back_populates='material_stocks')
    warehouse = db.relationship('Warehouse', back_populates='material_stocks')

    def __repr__(self):
        return f"<MaterialStock {self.material_id} in Warehouse {self.warehouse_id}: {self.quantity}>"



class InventoryMovement(BaseModel):
    __tablename__ = 'inventory_movements'

    id = db.Column(db.Integer, primary_key=True)
    movement_type = db.Column(db.String(20), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('material_lots.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.today())
    note = db.Column(db.String(255))

    # Origen y destino
    origin_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True)
    destination_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True)

    lot = db.relationship('MaterialLot', back_populates='movements')
    origin_warehouse = db.relationship('Warehouse', foreign_keys=[origin_warehouse_id])
    destination_warehouse = db.relationship('Warehouse', foreign_keys=[destination_warehouse_id])


    def __repr__(self):
        return f"<InventoryMovement {self.movement_type} - {self.quantity} ({self.lot.material.code})>"



    

class ProductLot(db.Model):
    __tablename__ = 'product_lots'

    id = db.Column(db.Integer, primary_key=True)
    lot_number = db.Column(db.String(50), nullable=False)  # Ej: LOTE-2025-001
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)

    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)  # Coste promedio unitario
    production_order_id = db.Column(db.Integer, db.ForeignKey('production_orders.id'), nullable=False)

    # Estado logístico (nunca in_process!)
    status = db.Column(db.String(20), nullable=False, default='in_stock')  
    # Ejemplos: in_stock, delivered, rejected, returned

    received_date = db.Column(db.DateTime, default=datetime.today())

    # Relaciones
    product_variant = db.relationship('ProductVariant', back_populates='lots')
    warehouse = db.relationship('Warehouse', back_populates='product_lots')
    production_order = db.relationship('ProductionOrder', back_populates='product_lots')
    movements = db.relationship('ProductLotMovement', back_populates='product_lot', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<ProductLot {self.lot_number} - {self.product_variant.code} - {self.quantity}>"


class ProductLotMovement(db.Model):
    __tablename__ = 'product_lot_movements'

    id = db.Column(db.Integer, primary_key=True)
    product_lot_id = db.Column(db.Integer, db.ForeignKey('product_lots.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # IN, OUT, ADJUST
    quantity = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.today)
    note = db.Column(db.String(255))

    # Origen y destino físico
    origin_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True)
    destination_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True)

    product_lot = db.relationship('ProductLot', back_populates='movements')
    origin_warehouse = db.relationship('Warehouse', foreign_keys=[origin_warehouse_id])
    destination_warehouse = db.relationship('Warehouse', foreign_keys=[destination_warehouse_id])

    def __repr__(self):
        return f"<ProductLotMovement {self.movement_type} - {self.quantity} - Lot {self.product_lot.lot_number}>"


class ProductStock(db.Model):
    __tablename__ = 'product_stocks'

    id = db.Column(db.Integer, primary_key=True)
    product_variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0.0)

    __table_args__ = (
        db.UniqueConstraint('product_variant_id', 'warehouse_id', name='uq_product_stock_variant_warehouse'),
    )

    product_variant = db.relationship('ProductVariant', back_populates='product_stocks')
    warehouse = db.relationship('Warehouse', back_populates='product_stocks')

    def __repr__(self):
        return f"<ProductStock {self.product_variant_id} in Warehouse {self.warehouse_id}: {self.quantity}>"
    


# models/inventory_adjustment.py aun no implementado
from app import db
from datetime import datetime

class InventoryAdjustment(db.Model):
    __tablename__ = 'inventory_adjustments'

    id = db.Column(db.Integer, primary_key=True)
    inventory_movement_id = db.Column(db.Integer, db.ForeignKey('inventory_movements.id'), nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    quantity_adjusted = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    movement = db.relationship('InventoryMovement', backref='adjustment', uselist=False)

    def __repr__(self):
        return f"<InventoryAdjustment {self.id} - Qty: {self.quantity_adjusted}>"
