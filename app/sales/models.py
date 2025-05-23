from app import db

from ..common import BaseModel

from ..core.enums import OrderStatus


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
    order_id = db.Column(db.Integer, db.ForeignKey('sale_orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

    size = db.Column(db.Float)
    qty = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String())
    price = db.Column(db.Float, nullable=False)  # Guardar el precio en el momento de la venta
    discount = db.Column(db.Float, default=0.00)  # Descuento por unidad (opcional)

    order = db.relationship('SaleOrder', back_populates='order_products')
    products = db.relationship('Product', back_populates='sale_order')

    @property
    def subtotal(self):
        return (self.price - self.discount) * self.qty

    
    

class ProductPriceHistory(BaseModel):

    __tablename__ = 'product_price_history'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    price = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)  # Fecha desde la cual este precio es válido
    end_date = db.Column(db.Date, nullable=True)  # Fecha hasta cuando es válido. Si es NULL, es el precio actual.

    #product = db.relationship('Product', back_populates='price_history')


