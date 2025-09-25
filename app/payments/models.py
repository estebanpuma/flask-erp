from datetime import date

from sqlalchemy import Numeric

from app import db

from ..common import BaseModel, SoftDeleteMixin


class PaymentMethod(BaseModel, SoftDeleteMixin):
    __tablename__ = "payment_methods"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)


class PaymentAgreement(BaseModel):
    __tablename__ = "payment_agreements"

    id = db.Column(db.Integer, primary_key=True)
    sale_order_id = db.Column(
        db.Integer, db.ForeignKey("sale_orders.id"), nullable=False
    )

    amount = db.Column(db.Float, nullable=False)  # Cuota acordada
    expected_date = db.Column(db.Date, nullable=False)  # Fecha acordada de pago

    notes = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    sale_order = db.relationship("SaleOrder", back_populates="agreements")
    user = db.relationship("User", lazy="joined")


class PaymentTransaction(BaseModel):
    __tablename__ = "payment_transactions"

    id = db.Column(db.Integer, primary_key=True)
    sale_order_id = db.Column(
        db.Integer, db.ForeignKey("sale_orders.id"), nullable=False
    )

    amount = db.Column(Numeric(12, 2), nullable=False)  # Lo realmente pagado
    payment_date = db.Column(
        db.Date, nullable=False, default=date.today()
    )  # Fecha real del pago
    method_id = db.Column(
        db.Integer, db.ForeignKey("payment_methods.id"), nullable=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    notes = db.Column(db.String(255))

    sale_order = db.relationship("SaleOrder", back_populates="transactions")
    method = db.relationship("PaymentMethod")
    user = db.relationship("User", lazy="joined")
