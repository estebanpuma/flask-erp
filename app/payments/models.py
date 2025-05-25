from app import db

from ..common import BaseModel

from enum import Enum
from datetime import date


# 1. Enum de estados
class InstallmentStatus(Enum):
    PENDING = "Pendiente"
    PAID = "Pagado"
    PARTIALLY_PAID = "Parcialmente pagado"
    OVERDUE = "Atrasado"


# 2. PaymentMethod
class PaymentMethod(BaseModel):
    __tablename__ = 'payment_methods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    payment_plans = db.relationship('PaymentPlan', back_populates='payment_method')


# 3. PaymentPlan
class PaymentPlan(BaseModel):
    __tablename__ = 'payment_plans'

    id = db.Column(db.Integer, primary_key=True)
    sale_order_id = db.Column(db.Integer, db.ForeignKey('sale_orders.id'), nullable=False)

    total_amount = db.Column(db.Float, nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=False)
    total_installments = db.Column(db.Integer, nullable=True)

    sale_order = db.relationship('SaleOrder', back_populates='payment_plans', foreign_keys=[sale_order_id])
    payment_method = db.relationship('PaymentMethod', back_populates='payment_plans')
    installments = db.relationship('Installment', back_populates='payment_plan', cascade='all, delete-orphan')

    @property
    def total_remaining_amount(self):
        return sum(i.remaining_amount for i in self.installments)


# 4. Installment
class Installment(BaseModel):
    __tablename__ = 'installments'

    id = db.Column(db.Integer, primary_key=True)
    payment_plan_id = db.Column(db.Integer, db.ForeignKey('payment_plans.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default=InstallmentStatus.PENDING.value)
    
    paid_on = db.Column(db.Date, nullable=True)  # Fecha del último pago
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    payment_plan = db.relationship('PaymentPlan', back_populates='installments')
    user = db.relationship('User', backref='installments_paid', lazy='joined')  # Para trazabilidad

    @property
    def remaining_amount(self):
        return round(self.amount - self.paid_amount, 2)

    def mark_as_paid(self, user_id=None):
        self.status = InstallmentStatus.PAID.value
        self.paid_on = date.today()
        if user_id:
            self.user_id = user_id

    def mark_as_partially_paid(self, user_id=None):
        self.status = InstallmentStatus.PARTIALLY_PAID.value
        self.paid_on = date.today()
        if user_id:
            self.user_id = user_id

    def mark_as_overdue(self):
        self.status = InstallmentStatus.OVERDUE.value


class PaymentTransaction(BaseModel):
    __tablename__ = 'payment_transactions'

    id = db.Column(db.Integer, primary_key=True)
    payment_plan_id = db.Column(db.Integer, db.ForeignKey('payment_plans.id'), nullable=False)
    installment_id = db.Column(db.Integer, db.ForeignKey('installments.id'), nullable=True)

    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    notes = db.Column(db.String(255))

    payment_plan = db.relationship('PaymentPlan', backref='transactions')
    installment = db.relationship('Installment', backref='transactions')
    user = db.relationship('User', backref='transactions_recorded', lazy='joined')
    method = db.relationship('PaymentMethod')
