from ..common import BaseModel, SoftDeleteMixin

from app import db




# Tabla intermedia entre Product y Size
product_size_association = db.Table('product_size_association',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('size_id', db.Integer, db.ForeignKey('sizes.id'), primary_key=True)
)

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
    code = db.Column(db.String(50), nullable=False, unique=True)  # Código único del modelo
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    line_id = db.Column(db.Integer, db.ForeignKey('product_lines.id'), nullable=False)
    sub_line_id = db.Column(db.Integer, db.ForeignKey('product_sub_lines.id'), nullable=True)
    
    images = db.relationship('ProductImages', back_populates='product', cascade='all, delete-orphan')

    line = db.relationship('ProductLine', back_populates='products')
    sub_line = db.relationship('ProductSubLine', back_populates='products')
    colors = db.relationship('ProductColor', back_populates='product') 
    
    sizes = db.relationship('Size', secondary=product_size_association, back_populates='products')

    material_details = db.relationship('ProductMaterialDetail', back_populates='product', cascade="all, delete-orphan")

    sale_order = db.relationship('SaleOrderProduct', back_populates='products')
    price_history = db.relationship('ProductPriceHistory', back_populates='product')

    def __repr__(self):
        return f'<Product(code={self.code}, name={self.name})>'
    

class ProductImages(BaseModel):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_path = db.Column(db.String(), nullable=False)

    product = db.relationship('Product', back_populates='images')


class MaterialGroup(BaseModel):
    __tablename__ = 'material_groups'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(), nullable=True)
    materials = db.relationship('Material', back_populates='material_group')
    

class Material(BaseModel):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    material_group_id = db.Column(db.Integer, db.ForeignKey('material_groups.id'), nullable=True)
    type = db.Column(db.String(200), nullable=True)
    name = db.Column(db.String(200), nullable=False)  # Ejemplo: 'Cuero', 'Textil', 'Sintético'
    detail = db.Column(db.String(), nullable=True)
    unit = db.Column(db.String(), nullable=False)
    stock = db.Column(db.Float, nullable=True, default=0)

    product_material_details = db.relationship('ProductMaterialDetail', back_populates='material')
    material_group = db.relationship('MaterialGroup', back_populates='materials')


    def __repr__(self):
        return f'<Material(name={self.name})>'
    

class ProductMaterialDetail(BaseModel):
    __tablename__ = 'product_material_details'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    serie_id = db.Column(db.Integer, db.ForeignKey('size_series.id'), nullable=False)
    unit = db.Column(db.String(10), nullable=False)  # Ejemplo: 'kg', 'm', 'units'
    quantity = db.Column(db.Float, nullable=False, default=1.0)

    product = db.relationship('Product', back_populates='material_details')
    material = db.relationship('Material', back_populates='product_material_details')

    def __repr__(self):
        return f'<ProductMaterialDetail(product={self.product.name}, material={self.material.name}, quantity={self.quantity})>'
    

class Color(BaseModel):
    __tablename__ = 'colors'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)  # Ejemplo: 'Rojo', 'Azul', 'Negro'
    description = db.Column(db.String(), nullable=True)
    hex_value = db.Column(db.String(7), nullable=True)  # Ejemplo: '#FF5733'
    product_colors = db.relationship('ProductColor', back_populates='product_colors')

    def __repr__(self):
        return f'<Color: {self.code}-{self.name}>'
    
class ProductColor(BaseModel):
    __tablename__ = 'product_colors'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    color_id = db.Column(db.Integer, db.ForeignKey('colors.id'), nullable=False)

    product = db.relationship('Product', back_populates='colors')
    product_colors = db.relationship('Color', back_populates='product_colors')

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

    products = db.relationship('Product', secondary=product_size_association, back_populates='sizes')

    def __repr__(self):
        return f'<Size(value={self.value})>'