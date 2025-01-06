from app.common.models import BaseModel, SoftDeleteMixin

from app import db


# Tabla de asociación entre ordernes de produccion y requerimientos de produccion
production_order_requirement = db.Table('production_order_requirement',
    db.Column('production_order_id', db.Integer, db.ForeignKey('production_orders.id', ondelete='CASCADE', onupdate='CASCADE'), 
              primary_key=True),
    db.Column('production_requirement_id', db.Integer, db.ForeignKey('production_requirements.id', ondelete='CASCADE', onupdate='CASCADE'),
               primary_key=True)
)


class ProductionOrder(BaseModel, SoftDeleteMixin):

    __tablename__ = 'production_orders'

    code = db.Column(db.String(50), nullable = False)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='Programada')
    scheduled_start_date = db.Column(db.DateTime)
    scheduled_end_date = db.Column(db.DateTime)
    actual_start_date = db.Column(db.DateTime, nullable=True)
    actual_end_date = db.Column(db.DateTime, nullable=True)
    #priority = db.Column(db.String(20), default='Media') Validar con logica del negocio del cliente
    notes = db.Column(db.String(500))

    production_requirements = db.relationship('ProductionRequirement', 
                                              secondary='production_order_requirement', 
                                              back_populates='production_order', 
                                              )
    
    consolidated_items = db.relationship('ConsolidatedProductionItem',
                                        back_populates='production_order',
                                        cascade='all, delete-orphan'
                                    )
    
    #status
    ORDER_STATUS = ['Programada', 'En progreso', 'Completada', 'Cancelada']
    #PRIORITY_LEVEL = ['Baja', 'Media', 'Alta']

    def set_order_status(self, status):
        if status not in self.ORDER_STATUS:
            raise ValueError(f'{status}, no es un estado valido')
        self.status = status
    

class ConsolidatedProductionItem(db.Model):
    __tablename__ = 'consolidated_production_items'

    id = db.Column(db.Integer, primary_key=True)
    production_order_id = db.Column(db.Integer, db.ForeignKey('production_orders.id', ondelete='CASCADE'), nullable=False)
    model_id = db.Column(db.Integer)
    model_code = db.Column(db.String(50), nullable=False)
    series_id = db.Column(db.Integer)
    series = db.Column(db.String(20), nullable=True)
    size = db.Column(db.Integer, nullable=True)
    total_quantity = db.Column(db.Integer, nullable=False, default=0)

    # Relación con la orden de producción
    production_order = db.relationship('ProductionOrder', back_populates='consolidated_items')

    
class ProductionRequirement(BaseModel, SoftDeleteMixin): 

    __tablename__ = 'production_requirements'
    
    type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pendiente')
    production_order = db.relationship('ProductionOrder', 
                                       secondary='production_order_requirement', 
                                       back_populates='production_requirements')

    __mapper_args__ = {
        'polymorphic_identity': 'requirement',  # Identidad para la clase base
        'polymorphic_on': type  # Campo que se usará para distinguir subclases
    }

    REQUIREMENT_STATUS = ['Programada', 'En progreso', 'Completada', 'Pendiente', 'Cancelada']

    def set_production_requiement_status(self, status):
        if status not in self.REQUIREMENT_STATUS:
            raise ValueError(f'{status}, no es parte de los estados permitidos')
    

class SaleProductionRequirement(ProductionRequirement): #request

    __tablename__ = 'sale_production_requirement'
    id = db.Column(db.Integer, db.ForeignKey('production_requirements.id'), primary_key=True)
    sale_order_id = db.Column(db.Integer, db.ForeignKey('sale_orders.id'), nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'sales_requirement'}


class StockProductionRequirement(ProductionRequirement):

    __tablename__ = 'stock_product_requirement'
    id = db.Column(db.Integer, db.ForeignKey('production_requirements.id'), primary_key=True)
    stock_order_id = db.Column(db.Integer, db.ForeignKey('stock_orders.id', ondelete='CASCADE'), nullable=False)
    # Relación bidireccional entre StockProductionBatch y StockOrderProductList
    stock_order = db.relationship('StockOrder', back_populates='stock_production_requirement')
    #parámetro cascade='all, delete-orphan' para que, si un StockProductionBatch es eliminado, sus elementos relacionados en StockOrderProductList también lo sean.

    __mapper_args__ = {'polymorphic_identity': 'stock_requirement'}


class StockOrder(BaseModel):

    __tablename__ = 'stock_orders'
    id = db.Column(db.Integer, primary_key=True)
    stock_order_code = db.Column(db.String(50), nullable=False, unique=True)
    request_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='Pendiente')
    notes = db.Column(db.String(), nullable=True)

    responsible = db.relationship('User')
    
    stock_order_product_list = db.relationship('StockOrderProductList', 
                                               back_populates='stock_order', 
                                               cascade='all, delete-orphan')
    stock_production_requirement = db.relationship('StockProductionRequirement',
                                                    back_populates='stock_order',
                                                    cascade='all, delete-orphan')
    
    

class StockOrderProductList(BaseModel):
    
    __tablename__ = 'stock_order_product_list'

    id = db.Column(db.Integer, primary_key=True)
    stock_order_id = db.Column(db.Integer, db.ForeignKey('stock_orders.id', ondelete='CASCADE'), 
                               nullable=False,
                               )
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_code = db.Column(db.String(50))
    product_serie = db.Column(db.String(20), nullable=False)
    product_size = db.Column(db.Integer, nullable=False)
    product_qty = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    stock_order = db.relationship('StockOrder', back_populates='stock_order_product_list')







