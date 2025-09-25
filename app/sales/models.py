from datetime import date
from decimal import Decimal

from sqlalchemy import Numeric

from app import db

from ..common import BaseModel
from ..core.enums import OrderStatus, PaymentStatus
from ..crm.models import Client as Client


class SaleOrder(BaseModel):
    __tablename__ = "sale_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True)
    order_date = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date)
    delivery_date = db.Column(db.Date)  # Para comparar cumplimiento vs promesa
    # Entrega
    shipping_province_id = db.Column(
        db.Integer, db.ForeignKey("provinces.id"), nullable=False
    )
    shipping_canton_id = db.Column(
        db.Integer, db.ForeignKey("cantons.id"), nullable=False
    )
    shipping_address = db.Column(db.String(250), nullable=False)
    shipping_reference = db.Column(db.String(250))
    # status
    status = db.Column(db.String(20), nullable=True, default=OrderStatus.DRAFT.value)
    payment_status = db.Column(
        db.String(20), nullable=False, default=PaymentStatus.UNPAID.value
    )

    subtotal = db.Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    discount_rate = db.Column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )  # Descuento global
    tax = db.Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    tax_rate = db.Column(Numeric(10, 2), nullable=False, default=Decimal("15.00"))
    total = db.Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    sales_person_id = db.Column(db.Integer, db.ForeignKey("workers.id"))

    salesperson = db.relationship("Worker", backref="sale_orders")
    client = db.relationship("Client", back_populates="orders", lazy="joined")

    amount_paid = db.Column(
        Numeric(12, 2), default=Decimal("0.00")
    )  # Pagos reales recibidos
    amount_due = db.Column(
        Numeric(12, 2), default=Decimal("0.00")
    )  # Lo que falta por cobrar

    lines = db.relationship(
        "SaleOrderLine",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    province = db.relationship("Provinces", back_populates="orders")
    canton = db.relationship("Cantons", back_populates="orders")
    agreements = db.relationship(
        "PaymentAgreement", back_populates="sale_order", cascade="all, delete-orphan"
    )
    transactions = db.relationship(
        "PaymentTransaction", back_populates="sale_order", cascade="all, delete-orphan"
    )

    canceled_reason = db.Column(db.String(200))
    notes = db.Column(db.String(250), nullable=True)

    def validate_status(self):
        if self.status not in [s.value for s in OrderStatus]:
            raise ValueError(f"Estado '{self.status}' no es válido.")


class SaleOrderLine(BaseModel):
    __tablename__ = "sale_order_lines"

    id = db.Column(db.Integer, primary_key=True)
    sale_order_id = db.Column(
        db.Integer, db.ForeignKey("sale_orders.id"), nullable=False
    )
    variant_id = db.Column(
        db.Integer, db.ForeignKey("product_variants.id"), nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False)
    price_unit = db.Column(Numeric(12, 2), nullable=False)
    discount_rate = db.Column(Numeric(12, 2), default=Decimal(0.00))
    cost_unit = db.Column(Numeric(12, 2))  # Opcional, útil para cálculo de margen

    order = db.relationship("SaleOrder", back_populates="lines")
    variant = db.relationship("ProductVariant")

    @property
    def subtotal(self):
        return (
            self.price_unit - (self.price_unit * self.discount_rate / 100)
        ) * self.quantity

    @property
    def line_discount(self):
        return (self.discount_rate / 100 * self.price_unit) * self.quantity


class SaleOrderPreview:
    def __init__(self, lines, discount_rate=0.0, tax_rate=0.0):
        self.lines = lines
        self.discount_rate = discount_rate
        self.tax_rate = tax_rate


class SaleOrderPreviewLine:
    def __init__(self, variant_id, quantity, price_unit, discount_rate=0.0):
        self.variant_id = variant_id
        self.quantity = quantity
        self.price_unit = price_unit
        self.discount_rate = discount_rate

    @property
    def subtotal(self):
        return (
            self.price_unit - (self.price_unit * self.discount_rate / 100)
        ) * self.quantity

    @property
    def line_discount(self):
        return (self.discount_rate / 100 * self.price_unit) * self.quantity
