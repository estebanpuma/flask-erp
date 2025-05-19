from app import db

from datetime import datetime

from ..common.models import BaseModel


class MaterialGroup(BaseModel):
    __tablename__ = 'material_groups'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(), nullable=True)
    materials = db.relationship('Material', back_populates='material_group')
    

class MaterialPriceHistory(BaseModel):
    __tablename__ = 'material_price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    price = db.Column(db.Float, nullable=False) 
    currency = db.Column(db.String(3), nullable=False, default='USD')
    start_date = db.Column(db.Date, nullable=False, default=datetime.today())
    end_date = db.Column(db.Date)  # Null = precio vigente
    is_actual_price = db.Column(db.Boolean, nullable=False, default=False)
    material = db.relationship('Material', back_populates='price_history')


class Material(BaseModel):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    material_group_id = db.Column(db.Integer, db.ForeignKey('material_groups.id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)  # Ej: Cuero, Sintético, Textil
    detail = db.Column(db.String(), nullable=True)
    unit = db.Column(db.String(10), nullable=False)
    stock = db.Column(db.Float, default=0)

    material_group = db.relationship('MaterialGroup', back_populates='materials')
    product_material_details = db.relationship('ProductVariantMaterialDetail', back_populates='material')
    price_history = db.relationship('MaterialPriceHistory', back_populates='material', order_by='MaterialPriceHistory.start_date.desc()')

    @property
    def current_price(self):
        return next(
            (ph.price for ph in self.price_history if ph.end_date is None),
            None
        )

    def __repr__(self):
        return f'<Material(name={self.name})>'