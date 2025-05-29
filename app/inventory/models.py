from app import db

from app.common.models import BaseModel, SoftDeleteMixin

from enum import Enum





class Warehouse(BaseModel, SoftDeleteMixin):
    __tablename__ = 'warehouses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(), nullable=True)
    location = db.Column(db.String(), nullable=True)

    # Relación con lotes
    lots = db.relationship('MaterialLot', back_populates='warehouse', lazy='dynamic')
    product_lots = db.relationship('ProductLot', back_populates='warehouse', lazy='dynamic')
    product_stocks = db.relationship('ProductStock', back_populates='warehouse')

    def __repr__(self):
        return f"<Warehouse {self.name}>"
    

