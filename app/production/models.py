from app.common.models import BaseModel, SoftDeleteMixin

from app import db


class ProductionOrder(BaseModel, SoftDeleteMixin):

    __tablename__ = 'production_orders'

    code = db.Column(db.String(50), nullable = False)
    status = db.Column(db.String(50), default='pending') 
    production_batches = db.relationship('ProductionBatch', back_populates='production_order', cascade='all, delete-orphan')
    status = db.Column(db.String(50), default='pending')
    

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

    __mapper_args__ = {'polymorphic_identity': 'sales_batch'}


class StockProductionBatch(ProductionBatch):

    __tablename__ = 'stock_product_batch'
    id = db.Column(db.Integer, db.ForeignKey('production_batches.id'), primary_key=True)
    stock_order_id = db.Column(db.Integer, db.ForeignKey('stock_orders.id'), nullable=False)
    # Relación bidireccional entre StockProductionBatch y StockOrderProductList
    stock_order = db.relationship('StockOrder', back_populates='stock_production_batch')
    #parámetro cascade='all, delete-orphan' para que, si un StockProductionBatch es eliminado, sus elementos relacionados en StockOrderProductList también lo sean.

    __mapper_args__ = {'polymorphic_identity': 'stock_batch'}


class StockOrder(BaseModel):

    __tablename__ = 'stock_orders'
    id = db.Column(db.Integer, primary_key=True)
    stock_order_code = db.Column(db.String(50), nullable=False, unique=True)
    request_date = db.Column(db.Date, nullable=False)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.String(), nullable=True)
    
    stock_order_product_list = db.relationship('StockOrderProductList', back_populates='stock_order')
    stock_production_batch = db.relationship('StockProductionBatch', back_populates='stock_order')
    

class StockOrderProductList(BaseModel):
    
    __tablename__ = 'stock_order_product_list'

    id = db.Column(db.Integer, primary_key=True)
    stock_order_id = db.Column(db.Integer, db.ForeignKey('stock_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_size = db.Column(db.Integer, nullable=False)
    product_qty = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    stock_order = db.relationship('StockOrder', back_populates='stock_order_product_list')







