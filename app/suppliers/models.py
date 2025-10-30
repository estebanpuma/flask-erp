from app import db

from ..common.models import BaseModel, SoftDeleteMixin


class SupplierContact(BaseModel):
    __tablename__ = "supplier_contacts"

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))  # Cargo (Ej: "Vendedor", "Gerente de Compras")
    email = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    is_primary = db.Column(db.Boolean, default=False)
    supplier = db.relationship("Supplier", back_populates="contacts")

    def __repr__(self):
        return f"<SupplierContact {self.name} for {self.supplier.name}>"


class Supplier(BaseModel, SoftDeleteMixin):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ruc_or_ci = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)

    material_lots = db.relationship(
        "MaterialLot", back_populates="supplier", lazy="dynamic"
    )

    contacts = db.relationship(
        "SupplierContact", back_populates="supplier", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Supplier {self.name}>"
