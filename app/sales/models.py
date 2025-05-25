from app import db

from ..common import BaseModel

from ..core.enums import OrderStatus

from datetime import datetime,date


class SaleOrder(BaseModel):
    __tablename__ = "sale_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True)
    order_date = db.Column(db.Date, default=date.today)
    delivery_date = db.Column(db.Date)
    actual_delivery_date = db.Column(db.Date)  # Para comparar cumplimiento vs promesa

    status = db.Column(db.String(20), nullable=False, default=OrderStatus.DRAFT.value)
    delivery_address = db.Column(db.String(200))

    subtotal = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)  # Descuento global
    tax = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)

    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    sales_person_id = db.Column(db.Integer, db.ForeignKey('salespersons.id'))

    salesperson = db.relationship('Salesperson', back_populates='sale_orders', lazy='joined')
    client = db.relationship('Client', back_populates='orders', lazy='joined')

    lines = db.relationship('SaleOrderLine', back_populates='order', cascade='all, delete-orphan', lazy='joined')
    payment_plans = db.relationship('PaymentPlan', back_populates='sale_order')

    canceled_reason = db.Column(db.String(200))
    notes = db.Column(db.String(250), nullable=True)

    @property
    def calculated_subtotal(self):
        return sum(line.subtotal for line in self.lines)

    @property
    def calculated_total(self):
        return self.calculated_subtotal - self.discount + self.tax

    def validate_status(self):
        if self.status not in [s.value for s in OrderStatus]:
            raise ValueError(f"Estado '{self.status}' no es válido.")


class SaleOrderLine(BaseModel):
    __tablename__ = 'sale_order_lines'

    id = db.Column(db.Integer, primary_key=True)
    sale_order_id = db.Column(db.Integer, db.ForeignKey('sale_orders.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    price_unit = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    cost_unit = db.Column(db.Float)  # Opcional, útil para cálculo de margen

    order = db.relationship('SaleOrder', back_populates='lines')
    variant = db.relationship('ProductVariant')

    @property
    def subtotal(self):
        return (self.price_unit - self.discount) * self.quantity

    

