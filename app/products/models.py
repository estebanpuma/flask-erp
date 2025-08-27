from ..common import BaseModel, SoftDeleteMixin
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date
from decimal import Decimal

from datetime import datetime

from app import db

from ..core.enums import SizeCategory
from ..common.models import AppSetting




class ProductLine(BaseModel, SoftDeleteMixin):
    __tablename__ = 'product_lines'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250))
    products = db.relationship('Product', back_populates='line', cascade='all, delete-orphan')

    collections = db.relationship('ProductCollection', back_populates='line', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ProductLine(name={self.name})>'


class ProductSubLine(BaseModel, SoftDeleteMixin):
    __tablename__ = 'product_sub_lines'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250))

    products = db.relationship('Product', back_populates='sub_line', cascade='all, delete-orphan')
    collections = db.relationship('ProductCollection', back_populates='sub_line', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ProductSubLine(name={self.name})>'
    

class ProductTarget(BaseModel, SoftDeleteMixin):
    __tablename__ = 'product_targets'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False)  # Ej. H, M, U, HN, MN, UN
    name = db.Column(db.String(50), nullable=False) 
    description = db.Column(db.String(255))

    collections = db.relationship('ProductCollection', back_populates='target', cascade='all, delete-orphan')
    products = db.relationship('Product', back_populates='target', cascade='all, delete-orphan')
    

class ProductCollection(BaseModel, SoftDeleteMixin):
    __tablename__ = 'product_collections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.Integer, nullable=False) # 1, 2, 3, 4
    aux_code = db.Column(db.String(10), nullable = True)

    line_id = db.Column(db.Integer, db.ForeignKey('product_lines.id'), nullable=False)
    subline_id = db.Column(db.Integer, db.ForeignKey('product_sub_lines.id'), nullable=True)
    target_id = db.Column(db.Integer, db.ForeignKey('product_targets.id'), nullable=False)

    description = db.Column(db.String(255))
    n_hormas = db.Column(db.Integer, nullable=True, default=0)
    image_url = db.Column(db.String(255))

    line = db.relationship('ProductLine', back_populates='collections')
    sub_line = db.relationship('ProductSubLine', back_populates='collections')
    target = db.relationship('ProductTarget', back_populates='collections')
    

    products = db.relationship('Product', back_populates='collection', cascade='all, delete-orphan')
    

    


class Product(BaseModel, SoftDeleteMixin):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # Ej: CDU101
    #number = db.Column = (db.Integer, nullable=False)

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    line_id = db.Column(db.Integer, db.ForeignKey('product_lines.id'), nullable=False)
    subline_id = db.Column(db.Integer, db.ForeignKey('product_sub_lines.id'), nullable=True)
    target_id = db.Column(db.Integer, db.ForeignKey('product_targets.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('product_collections.id'), nullable=False)

    line = db.relationship('ProductLine', back_populates='products')
    sub_line = db.relationship('ProductSubLine', back_populates='products')
    target = db.relationship('ProductTarget', back_populates='products')
    collection = db.relationship('ProductCollection', back_populates='products')

    images = db.relationship('ProductImage', back_populates='product', cascade='all, delete-orphan')
    designs = db.relationship('ProductDesign', back_populates='product', cascade='all, delete-orphan')

    @property
    def current_price(self):
        return next((ph.price for ph in self.price_history if ph.end_date is None), None)

    def __repr__(self):
        return f'<Producto: {self.name}>'


product_design_colors = db.Table(
    'product_design_colors',
    db.Column('design_id', db.Integer, db.ForeignKey('product_designs.id'), primary_key=True),
    db.Column('color_id', db.Integer, db.ForeignKey('colors.id'), primary_key=True)
)

class ProductDesign(BaseModel, SoftDeleteMixin):
    __tablename__ = 'product_designs'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    code = db.Column(db.String(50), nullable=False)  # Ej: C001NE
    name = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(255))

    current_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    # override manual opcional
    manual_price = db.Column(db.Numeric(12, 2), nullable=True)

    # opcional: flag para indicar override
    use_manual_price = db.Column(db.Boolean, nullable=False, default=False, server_default=sa.text('false'))

    price_history = db.relationship(
        'ProductPriceHistory',
        back_populates='design',
        order_by='ProductPriceHistory.created_at.desc()',
        cascade='all, delete-orphan'
    )

    product = db.relationship('Product', back_populates='designs')
    colors = db.relationship('Color', secondary=product_design_colors, backref='designs')
    variants = db.relationship('ProductVariant', back_populates='design', cascade='all, delete-orphan')
    images = db.relationship('DesignImage', back_populates='design', cascade='all, delete-orphan')


class ProductVariant(BaseModel, SoftDeleteMixin):
    __tablename__ = 'product_variants'

    id = db.Column(db.Integer, primary_key=True)
    design_id = db.Column(db.Integer, db.ForeignKey('product_designs.id'), nullable=False)
    size_id = db.Column(db.Integer, db.ForeignKey('sizes.id'), nullable=False)

    code = db.Column(db.String(50), unique=True, nullable=False)  # Ej: C001NE40
    barcode = db.Column(db.String(50), unique=True)
    stock = db.Column(db.Integer, default=0)

    standar_time = db.Column(db.Numeric(12,3), nullable=True, default=0.00)

    design = db.relationship('ProductDesign', back_populates='variants')
    size = db.relationship('Size')
    materials = db.relationship('ProductVariantMaterialDetail', back_populates='variant', cascade='all, delete-orphan')
    lots = db.relationship('ProductLot', back_populates='product_variant', lazy='dynamic')
    product_stocks = db.relationship('ProductStock', back_populates='product_variant', cascade='all, delete-orphan')

    operations      = db.relationship('ProductVariantOperationDetail', back_populates='variant')

    __table_args__ = (
        db.UniqueConstraint('design_id', 'size_id', 'code', name='uq_product_variant_code'),
    )

     

    @property
    def labor_cost_today(self) -> Decimal:
        return self.labor_cost()

    # ——— 3. Costo unitario completo ———
    def unit_cost(self, *, as_of: date | None = None) -> Decimal:
        ref = as_of or date.today()

        mat_cost = sum(
            det.quantity * det.material.current_avg_cost(ref)
            for det in self.materials
        )

        labor_cost = self.labor_cost(as_of=ref)
        overhead = 0

        return mat_cost + labor_cost + overhead


class ProductVariantOperationDetail(db.Model):
    __tablename__ = "variant_operations"
    id                   = db.Column(db.Integer, primary_key=True)
    variant_id           = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=False)
    operation_id         = db.Column(db.Integer, db.ForeignKey("operations.id"),      nullable=False)

    #orden y paralelos
    sequence             = db.Column(db.Integer, default=10, nullable=False) #10,20,30
    group_number         = db.Column(db.Integer, default=1, nullable=False) #paralelos dentro de la misma sequence

    # TIEMPOS DEL ESTUDIO (por esta variante en esta operación)
    cycle_min            = db.Column(db.Numeric(8,3), nullable=False)         # tiempo estándar unitario
    setup_min            = db.Column(db.Numeric(8,3), default=0)              # por lote (opcional)
    batch_size           = db.Column(db.Integer)                              # p.ej. 20 (opcional)

    date_from            = db.Column(db.Date, default=date.today, nullable=False)
    date_to              = db.Column(db.Date, nullable=True)         # NULL = vigente

    variant              = db.relationship("ProductVariant", back_populates="operations")
    operation            = db.relationship("Operations", back_populates="variant_operations")
    resources            = db.relationship(
                                            "VariantOperationResource",
                                            back_populates="variant_operation",
                                            cascade="all, delete-orphan",
                                            passive_deletes=True
                                        )
                                    


    __table_args__ = (
        db.UniqueConstraint('variant_id','operation_id','date_from', name='uq_variant_op_since'),
        db.Index('ix_variant_seq', 'variant_id', 'sequence'),
    )
    



class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id           = db.Column(db.Integer, primary_key=True)
    product_id   = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    filename     = db.Column(db.String(255), nullable=False)
    is_primary   = db.Column(db.Boolean, default=False)
    uploaded_at  = db.Column(db.DateTime, default=datetime.now)
    order = db.Column(db.Integer, default=0)

    product = db.relationship('Product', back_populates='images')
    @property
    def url(self):
        # asume que usas send_from_directory en /api/v1/products/<id>/images/<filename>
        return f"/api/v1/products/{self.product_id}/images/{self.filename}"



class DesignImage(BaseModel):
    __tablename__ = 'design_images'

    id = db.Column(db.Integer, primary_key=True)
    design_id = db.Column(db.Integer, db.ForeignKey('product_designs.id'))
    is_primary   = db.Column(db.Boolean, default=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)

    design = db.relationship('ProductDesign', back_populates='images')
    @property
    def url(self):
        # asume que usas send_from_directory en /api/v1/products/<id>/images/<filename>
        return f"/api/v1/product-designs/{self.design_id}/images/{self.filename}"

    def __repr__(self):
        return f'<ProductVariantImage(variant_id={self.design_id}, file={self.filename})>'


class ProductVariantMaterialDetail(BaseModel):
    __tablename__ = 'product_variant_material_details'

    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    variant = db.relationship('ProductVariant', back_populates='materials')
    material = db.relationship('Material')

    __table_args__ = (
        db.UniqueConstraint('variant_id', 'material_id', name='uq_variant_material'),
    )


class ProductPriceHistory(BaseModel, SoftDeleteMixin):
    __tablename__ = 'product_price_history'

    id = db.Column(db.Integer, primary_key=True)
    design_id = db.Column(
        db.Integer,
        db.ForeignKey('product_designs.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    # Costos directos y indirectos
    direct_cost   = db.Column(db.Numeric(12, 2), nullable=False)  # p.ej. 12345.67
    indirect_cost = db.Column(db.Numeric(12, 2), nullable=False)

    # Porcentaje de markup aplicado (0.00–1.00 → 0%–100%)
    markup_pct    = db.Column(db.Numeric(5, 4), nullable=False)

    override = db.Column(db.Boolean, nullable=False, default=False, server_default=sa.text('false'))

    # Precio neto resultante (sin impuestos)
    price_net     = db.Column(db.Numeric(12, 2), nullable=False)

    # Timestamp automático
    created_at    = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
        index=True
    )

    # Relación inversa
    design = db.relationship(
        'ProductDesign',
        back_populates='price_history',
        lazy='joined'
    )



class Color(BaseModel):
    __tablename__ = 'colors'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), nullable=False)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String())
    hex_value = db.Column(db.String(7))

    def __repr__(self):
        return f'<Color: {self.code}-{self.name}>'


class Size(BaseModel):
    __tablename__ = 'sizes'
    
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(10), nullable=False)  # hombre, mujer, niño
    length = db.Column(db.Float, nullable=True)
    width = db.Column(db.Float, nullable=True)
    __table_args__ = (
        db.UniqueConstraint('value', 'category', name='uq_size_value_category'),
    )

series_sizes = db.Table(
    'series_sizes',
    db.Column('series_id', db.Integer, db.ForeignKey('size_series.id'), primary_key=True),
    db.Column('size_id', db.Integer, db.ForeignKey('sizes.id'), primary_key=True)
)

class SizeSeries(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    start_size = db.Column(db.Integer, nullable=False)
    end_size = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(20), nullable=False)  # 'hombre', 'mujer', 'niño'

    sizes = db.relationship('Size', secondary=series_sizes, backref='series')

    def validate_category(self):
        if self.category not in [s.value for s in SizeCategory]:
            raise ValueError(f"Categoria '{self.category}' no es válido.")