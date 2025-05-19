from ..common import BaseModel, SoftDeleteMixin

from datetime import datetime

from app import db



class ProductLine(BaseModel, SoftDeleteMixin):

    __tablename__ = 'product_lines'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=False)
    description = db.Column(db.String(250), nullable=True)

    products = db.relationship('Product', back_populates='line', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ProductLine(name={self.name})>'
    

class ProductSubLine(BaseModel, SoftDeleteMixin):
    __tablename__ = 'product_sub_lines'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False, unique=False)
    description = db.Column(db.String(250), nullable=True)
    products = db.relationship('Product', back_populates='sub_line', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ProductSubLine(name={self.name})>'

    
class Product(BaseModel, SoftDeleteMixin):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # Ej: C001
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    line_id = db.Column(db.Integer, db.ForeignKey('product_lines.id'), nullable=True)
    sub_line_id = db.Column(db.Integer, db.ForeignKey('product_sub_lines.id'), nullable=True)

    line = db.relationship('ProductLine', back_populates='products')
    sub_line = db.relationship('ProductSubLine', back_populates='products')
    variants = db.relationship('ProductVariant', back_populates='product', cascade='all, delete-orphan')
    

    @property
    def current_price(self):
        return next((ph.price for ph in self.price_history if ph.end_date is None), None)
    
    def __repr__(self):
        return f'<Producto: {self.name}>'
    

class ProductVariant(BaseModel):
    __tablename__ = 'product_variants'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    size_id = db.Column(db.Integer, db.ForeignKey('sizes.id'), nullable=False)

    code = db.Column(db.String(50), unique=True, nullable=False)  # Ej: C001NEBL
    barcode = db.Column(db.String(50), unique=True)
    stock = db.Column(db.Float, default=0)

    images = db.relationship('ProductVariantImage', back_populates='variant', cascade='all, delete-orphan')
    product = db.relationship('Product', back_populates='variants')
    size = db.relationship('Size')
    colors = db.relationship('Color', secondary='product_variant_colors', backref='variants')
    materials = db.relationship('ProductVariantMaterialDetail', back_populates='variant', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('product_id', 'size_id', 'code', name='uq_product_variant_code'),
    )


class ProductVariantColor(BaseModel):
    __tablename__ = 'product_variant_colors'

    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    color_id = db.Column(db.Integer, db.ForeignKey('colors.id'), nullable=False)    


class ProductVariantImage(BaseModel):
    __tablename__ = 'product_variant_images'

    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)  # Ej: "abc123.webp"
    file_path = db.Column(db.String(255), nullable=False)  # Ej: "/static/media/products/..."
    order = db.Column(db.Integer, default=0)

    variant = db.relationship('ProductVariant', back_populates='images')

    def __repr__(self):
        return f'<ProductVariantImage(variant_id={self.variant_id}, file={self.file_name})>'


class ProductVariantMaterialDetail(BaseModel):
    __tablename__ = 'product_variant_material_details'

    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    
    serie_id = db.Column(db.Integer, db.ForeignKey('size_series.id'), nullable=False)
    
    quantity = db.Column(db.Float, nullable=False)

    variant = db.relationship('ProductVariant', back_populates='materials')
    material = db.relationship('Material')
    
    serie = db.relationship('SizeSeries')

    __table_args__ = (
        db.UniqueConstraint('variant_id', 'material_id', 'serie_id', name='uq_variant_material_color_serie'),
    )



class Color(BaseModel):
    __tablename__ = 'colors'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)  # Ejemplo: 'Rojo', 'Azul', 'Negro'
    description = db.Column(db.String(), nullable=True)
    hex_value = db.Column(db.String(7), nullable=True)  # Ejemplo: '#FF5733'
    

    def __repr__(self):
        return f'<Color: {self.code}-{self.name}>'
    


class SizeSeries(BaseModel, SoftDeleteMixin):
    __tablename__ = 'size_series'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # Ejemplo: 'Serie 1', 'Serie 2'
    description = db.Column(db.String(200), nullable=True)
    start_size = db.Column(db.Integer, nullable=False)
    end_size = db.Column(db.Integer, nullable=False)
    sizes = db.relationship('Size', back_populates='series', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<SizeSeries(name={self.name})>'


class Size(BaseModel):
    __tablename__ = 'sizes'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(10), nullable=False)  # Ejemplo: '40', 'M', '10'
    
    series_id = db.Column(db.Integer, db.ForeignKey('size_series.id'), nullable=False )
    series = db.relationship('SizeSeries', back_populates='sizes')


    def __repr__(self):
        return f'<Size(value={self.value})>'