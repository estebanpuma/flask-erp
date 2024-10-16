from app import db

from ..common import BaseModel


class PaymentMethod(BaseModel):

    __tablename__ = 'payment_methods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    payment_plans = db.relationship('PaymentPlan', back_populates='payment_method')


class PaymentPlan(BaseModel):

    __tablename__ = 'payment_plans'

    id = db.Column(db.Integer, primary_key=True)
    sale_order_id = db.Column(db.Integer, db.ForeignKey('sale_orders.id'))

    total_amount = db.Column(db.Float, nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'))
    total_installments = db.Column(db.Integer, nullable=True)
    
    sale_order = db.relationship('SaleOrder', back_populates='payment_plans', foreign_keys=[sale_order_id])
    payment_method = db.relationship('PaymentMethod', back_populates='payment_plans')
    installments = db.relationship('Installment', back_populates='payment_plan', cascade='all, delete-orphan')

    @property
    def total_remaining_amount(self):
        """Calcula el monto total pendiente de pago en todas las cuotas."""
        return sum(installment.remaining_amount for installment in self.installments)
    

class Installment(BaseModel):
    __tablename__ = 'installments'
    id = db.Column(db.Integer, primary_key=True)
    payment_plan_id = db.Column(db.Integer, db.ForeignKey('payment_plans.id'))
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Pending')  # Estado del pago
    
    payment_plan = db.relationship('PaymentPlan', back_populates='installments')

    @property
    def remaining_amount(self):
        """Calcula el monto restante por pagar."""
        return self.amount - self.paid_amount

    def mark_as_paid(self):
        self.status = 'Paid'

    def mark_as_overdue(self):
        self.status = 'Overdue'

    def mark_as_partially_paid(self):
        self.status = 'Partially Paid'