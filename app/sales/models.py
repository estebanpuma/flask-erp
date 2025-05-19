from app import db

from ..common import BaseModel

from ..core.enums import OrderStatus

from datetime import datetime


class SaleOrder(BaseModel):

    __tablename__ = "sale_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True)
    order_date = db.Column(db.Date)
    delivery_date = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False, default=OrderStatus.DRAFT.value)
    delivery_address = db.Column(db.String(200))

    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    sales_person_id = db.Column(db.Integer, db.ForeignKey('salespersons.id'))
    
    salesperson = db.relationship('Salesperson', back_populates='sale_orders', lazy='joined')
    client = db.relationship('Client', back_populates='orders', lazy='joined')
    order_products = db.relationship('SaleOrderProduct', back_populates='order', cascade='all, delete-orphan', lazy='joined' )
    payment_plans = db.relationship('PaymentPlan', back_populates='sale_order')

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.order_products)
    
    def validate_status(self):
        if self.status not in [s.value for s in OrderStatus]:
            raise ValueError(f"Estado '{self.status}' no es válido.")
    

class SaleOrderProduct(BaseModel):
    __tablename__ = 'sale_order_products'

    id = db.Column(db.Integer, primary_key=True)
    sale_order_id = db.Column(db.Integer, db.ForeignKey('sale_orders.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_unit = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.00)  # Descuento por unidad (opcional)

    order = db.relationship('SaleOrder', back_populates='order_products')

    variant = db.relationship('ProductVariant')

    @property
    def subtotal(self):
        return (self.price - self.discount) * self.qty

    
    

class ProductPriceHistory(BaseModel):
    __tablename__ = 'product_price_history'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    start_date = db.Column(db.Date, nullable=False, default=datetime.today())
    end_date = db.Column(db.Date)
    is_actual_price = db.Column(db.Boolean, default=False)

    product = db.relationship('Product', backref='price_history')



