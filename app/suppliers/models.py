from app import db

from ..common.models import BaseModel

class Supplier(BaseModel):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ruc_or_ci = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    material_lots = db.relationship('MaterialLot', back_populates='supplier', lazy='dynamic')


    def __repr__(self):
        return f"<Supplier {self.name}>"