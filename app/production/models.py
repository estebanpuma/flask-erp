from app.common.models import BaseModel, SoftDeleteMixin

from ..core.enums import OrderStatus

from app import db

from ..core.origin_factory import OriginFactory

class ProductionOrder(db.Model):
    __tablename__ = "production_orders"

    id = db.Column(db.Integer, primary_key=True)
    production_request_id = db.Column(db.Integer, db.ForeignKey("production_requests.id"), nullable=False)
    status = db.Column(db.String(50), default=OrderStatus.DRAFT.value) 
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    total_man_hours = db.Column(db.Float)

    created_at = db.Column(db.Date)

    production_request = db.relationship("ProductionRequest", backref="production_orders")
    lines = db.relationship("ProductionOrderLine", backref="production_order", cascade="all, delete-orphan")


class ProductionOrderLine(db.Model):
    __tablename__ = "production_order_lines"

    id = db.Column(db.Integer, primary_key=True)
    production_order_id = db.Column(db.Integer, db.ForeignKey("production_orders.id"), nullable=False)
    product_variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=False)
    size_id = db.Column(db.Integer, db.ForeignKey("sizes.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    estimated_hours = db.Column(db.Float)

    product_variant = db.relationship("ProductVariant")
    size = db.relationship("Size")
    checkpoints = db.relationship("ProductionCheckpoint", backref="order_line", cascade="all, delete-orphan")
    materials = db.relationship("ProductionMaterialDetail", backref="order_line", cascade="all, delete-orphan")


class ProductionCheckpoint(db.Model):
    __tablename__ = "production_checkpoints"

    id = db.Column(db.Integer, primary_key=True)
    order_line_id = db.Column(db.Integer, db.ForeignKey("production_order_lines.id"), nullable=False)
    stage = db.Column(db.String(20))  # corte, aparado, armado, terminado
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)


class ProductionMaterialDetail(db.Model):
    __tablename__ = "production_material_details"

    id = db.Column(db.Integer, primary_key=True)
    order_line_id = db.Column(db.Integer, db.ForeignKey("production_order_lines.id"), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False)
    quantity_needed = db.Column(db.Float)
    waste_percentage = db.Column(db.Float, default=5.0)  # Porcentaje de desperdicio
    quantity_reserved = db.Column(db.Float, default=0.0)
    quantity_delivered = db.Column(db.Float, default=0.0)

    material = db.relationship("Material")


class ProductionMaterialSummary(BaseModel):
    __tablename__ = "production_material_summaries"

    id = db.Column(db.Integer, primary_key=True)
    production_order_id = db.Column(db.Integer, db.ForeignKey("production_orders.id"), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False)
    total_quantity_needed = db.Column(db.Float, nullable=False)
    quantity_reserved = db.Column(db.Float, default=0.0)
    quantity_pending = db.Column(db.Float, default=0.0)  # lo que falta reservar (útil para sugerir compras)

    material = db.relationship("Material")
    production_order = db.relationship("ProductionOrder", backref="material_summaries")


class ManHourEstimate(db.Model):
    __tablename__ = "man_hour_estimates"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    hours_per_unit = db.Column(db.Float, nullable=False)

    product = db.relationship("Product")


class ProductionRework(db.Model):
    __tablename__ = "production_reworks"

    id = db.Column(db.Integer, primary_key=True)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey("production_checkpoints.id"), nullable=False)
    reason = db.Column(db.String(255))
    additional_hours = db.Column(db.Float)
    additional_materials = db.Column(db.Boolean, default=False)

    checkpoint = db.relationship("ProductionCheckpoint")
    rework_materials = db.relationship("ProductionMaterialDetailForRework", backref="rework", cascade="all, delete-orphan")


class ProductionMaterialDetailForRework(db.Model):
    __tablename__ = "production_material_detail_for_reworks"

    id = db.Column(db.Integer, primary_key=True)
    rework_id = db.Column(db.Integer, db.ForeignKey("production_reworks.id"), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"), nullable=False)
    quantity_used = db.Column(db.Float, nullable=False)

    material = db.relationship("Material")



class ProductionRequest(BaseModel):
    __tablename__ = "production_requests"

    id = db.Column(db.Integer, primary_key=True)
    origin_type = db.Column(db.String(50))  # 'sale_order', 'rd_order', 'stock_order', etc.
    origin_id = db.Column(db.Integer)       # ID dinámico según el tipo
    purpose = db.Column(db.String(100))
    title = db.Column(db.String(100))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


    created_by = db.relationship("User")

    @property
    def origin_obj(self):
        return OriginFactory.get_origin(self.origin_type, self.origin_id)

