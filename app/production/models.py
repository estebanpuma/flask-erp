from app.common.models import BaseModel, SoftDeleteMixin

from app import db


class ProductionOrder(BaseModel, SoftDeleteMixin):

    __tablename__ = 'production_orders'

    code = db.Column(db.String(50), nullable = False)
    status = db.Column(db.String(50), default='pending') 
    production_batches = db.relationship('ProductionBatch', back_populates='production_order', cascade='all, delete-orphan')
    status = db.Column(db.String(50), default='pending')

    bom = db.relationship('BillOfMaterials', back_populates='production_order', uselist=False)
    

class ProductionBatch(BaseModel, SoftDeleteMixin):

    __tablename__ = 'production_batches'

    code = db.Column(db.String(50), nullable = False)
    batch_type = db.Column(db.String(50))
    is_supervised = db.Column(db.Boolean, default=False)  # Indica si fue supervisado
    status = db.Column(db.String(50), default='pending')
    production_order_id = db.Column(db.Integer, db.ForeignKey('production_orders.id'), nullable=False)
    
    production_order = db.relationship('ProductionOrder', back_populates='production_batches')
    

    __mapper_args__ = {
        'polymorphic_identity': 'batch',  # Identidad para la clase base
        'polymorphic_on': batch_type  # Campo que se usará para distinguir subclases
    }
    

class SaleProductionBatch(ProductionBatch):

    __tablename__ = 'sale_production_batch'
    id = db.Column(db.Integer, db.ForeignKey('production_batches.id'), primary_key=True)
    sale_order_code = db.Column(db.String(50), db.ForeignKey('sale_orders.order_number'), nullable=False)
    products_list = db.relationship('SaleOrderProductList')

    __mapper_args__ = {'polymorphic_identity': 'sales_batch'}


class StockProductionBatch(ProductionBatch):

    __tablename__ = 'stock_product_batch'
    id = db.Column(db.Integer, db.ForeignKey('production_batches.id'), primary_key=True)
    stock_order_code = db.Column(db.String(50), db.ForeignKey('stock_orders.stock_order_code'), nullable=False)
    # Relación bidireccional entre StockProductionBatch y StockOrderProductList
    products_list = db.relationship('StockOrderProductList', back_populates='stock_production_batch', cascade='all, delete-orphan')
    #parámetro cascade='all, delete-orphan' para que, si un StockProductionBatch es eliminado, sus elementos relacionados en StockOrderProductList también lo sean.

    __mapper_args__ = {'polymorphic_identity': 'stock_batch'}


class StockOrderProductList(BaseModel):
    
    __tablename__ = 'stock_order_product_list'

    stock_order = db.Column(db.String(50), db.ForeignKey('stock_orders.stock_order_code'), nullable=False)
    stock_production_batch_id = db.Column(db.Integer, db.ForeignKey('stock_product_batch.id'))
    stock_production_batch = db.relationship('StockProductionBatch', back_populates='products_list')  # Relación bidireccional
    product_code = db.Column(db.String(50), db.ForeignKey('products.code'), nullable=False)
    product_size = db.Column(db.Integer, nullable=False)
    product_qty = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)


class StockOrder(BaseModel):

    __tablename__ = 'stock_orders'

    stock_order_code = db.Column(db.String(50), nullable=False, unique=True)
    stock_order_product_list = db.relationship('StockOrderProductList')


class SaleOrderProductList(BaseModel):

    __tablename__ = 'sale_order_product_list'

    sale_production_batch_id = db.Column(db.Integer, db.ForeignKey('sale_production_batch.id'))
    sale_production_batch = db.relationship('SaleProductionBatch', back_populates='products_list') 

    sale_order_code = db.Column(db.String(50), db.ForeignKey('sale_orders.order_number'), nullable=False)
    product_code = db.Column(db.String(50), db.ForeignKey('products.code'), nullable=False)
    product_size = db.Column(db.Integer, nullable=False)
    product_qty = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)


class BillOfMaterials(BaseModel):
    __tablename__ = 'bill_of_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    materials = db.relationship('BOMMaterial', back_populates='bom', cascade='all, delete-orphan')
    production_order_id = db.Column(db.Integer, db.ForeignKey('production_orders.id'), nullable=True)  # Si aplica a la producción general
    production_batch_id = db.Column(db.Integer, db.ForeignKey('production_batches.id'), nullable=True)  # Si aplica a un lote específico
    production_order = db.relationship('ProductionOrder', back_populates='bom')


class BOMMaterial(BaseModel):
    __tablename__ = 'bom_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    material_code = db.Column(db.String(50), db.ForeignKey('materials.code'), nullable=False, unique=True)
    material_unit = db.Column(db.String())
    material_qty = db.Column(db.Float, nullable=False)
    bom_id = db.Column(db.Integer, db.ForeignKey('bill_of_materials.id'), nullable=False)
    bom = db.relationship('BillOfMaterials', back_populates='materials')
    material = db.relationship('Material')
