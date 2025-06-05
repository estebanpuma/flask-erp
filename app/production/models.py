from app.common.models import BaseModel, SoftDeleteMixin

from ..core.enums import OrderStatus

from app import db

from datetime import datetime

from ..core.origin_factory import OriginFactory



# Tabla intermedia para relación muchos a muchos
production_order_requests = db.Table(
    "production_order_requests",
    db.Column("production_order_id", db.Integer, db.ForeignKey("production_orders.id", ondelete='CASCADE')),
    db.Column("production_request_id", db.Integer, db.ForeignKey("production_requests.id"))
)

class ProductionOrder(db.Model):
    __tablename__ = "production_orders"


    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(15), unique=True, nullable=False)
    status = db.Column(db.String(50), default=OrderStatus.DRAFT.value) 
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    created_at = db.Column(db.Date, default = datetime.today())

    estimated_man_hours = db.Column(db.Float, nullable=True, default=0.0)

    # Planificación global de mano de obra
    workers_assigned = db.Column(db.Integer, default=1)   # Total trabajadores en la orden
    total_overtime_hours = db.Column(db.Float, default=0.0)     # Horas extra global para todos los trabajadores

    lines = db.relationship("ProductionOrderLine", backref="production_order", cascade="all, delete-orphan")
    material_summaries = db.relationship("ProductionMaterialSummary", backref="production_order", cascade="all, delete-orphan")
    events = db.relationship("ProductionEvent", backref="production_order", cascade="all, delete-orphan")
    plan_change_logs = db.relationship("PlanChangeLog", backref="production_order", cascade="all, delete-orphan")

    production_requests = db.relationship(
        "ProductionRequest",
        secondary=production_order_requests,
        backref="production_orders",
    )
    product_lots = db.relationship('ProductLot', back_populates='production_order', lazy='dynamic')

    @property
    def get_production_duration_days(self):
        from .entities import ProductionOrderEntity
        days = ProductionOrderEntity(self).get_production_duration_days
        return days


class ProductionOrderLine(db.Model):
    __tablename__ = "production_order_lines"

    id = db.Column(db.Integer, primary_key=True)
    production_order_id = db.Column(db.Integer, db.ForeignKey("production_orders.id"), nullable=False)
    product_variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    quantity = db.Column(db.Integer, nullable=False)

    estimated_man_hours = db.Column(db.Float, nullable=True, default=0)

    # Planificación de mano de obra a nivel de línea
    workers_assigned = db.Column(db.Integer, default=1)
    overtime_hours = db.Column(db.Float, default=0.0)

    product_variant = db.relationship("ProductVariant")
   
    checkpoints = db.relationship("ProductionCheckpoint", backref="order_line", cascade="all, delete-orphan")
    materials = db.relationship("ProductionMaterialDetail", backref="order_line", cascade="all, delete-orphan")

    def __repr__(self):
        return super().__repr__()


class ProductionLineWorkLog(BaseModel):

    __tablename__ = 'production_line_work_logs'

    id = db.Column(db.Integer, primary_key=True)
    production_order_line_id = db.Column(db.Integer, db.ForeignKey("production_order_lines.id"), nullable=False)
    log_date = db.Column(db.Date)
    shift_name = db.Column(db.String(), nullable=True) #manana/tarde/noche
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    entries = db.relationship('WorkLogEntry', back_populates='production_line_work_log', cascade='all, delete-orphan')


class WorkLogEntry(BaseModel):

    __tablename__ = 'work_log_entries'

    id = db.Column(db.Integer, primary_key=True)
    production_line_work_log_id = db.Column(db.Integer, db.ForeignKey("production_line_work_logs.id"), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"), nullable=False)
    normal_hours_worked = db.Column(db.Float, default=0.0)
    overtime_hours_worked = db.Column(db.Float, default=0.0)
    comment = db.Column(db.String(), nullable=True)

    production_line_work_log = db.relationship('ProductionLineWorkLog', back_populates='entries')

    worker = db.relationship('Worker', backref='work_log')


class ProductionRequest(BaseModel):
    __tablename__ = "production_requests"

    id = db.Column(db.Integer, primary_key=True)
    origin_type = db.Column(db.String(50))  # 'sale_order', 'rdi_order', 'stock_order'
    origin_id = db.Column(db.Integer)       # ID dinámico según el tipo
    purpose = db.Column(db.String(100))
    title = db.Column(db.String(100))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default=OrderStatus.PENDING.value)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


    created_by = db.relationship("User")

    @property
    def origin_obj(self):
        return OriginFactory.get_origin(self.origin_type, self.origin_id)
    

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
    #production_order = db.relationship("ProductionOrder", backref="material_summaries")


class ManHourEstimate(db.Model):
    __tablename__ = "man_hour_estimates"

    id = db.Column(db.Integer, primary_key=True)
    product_variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=False)
    hours_per_unit = db.Column(db.Float, nullable=False)

    valid_from = db.Column(db.Date, nullable=False, default=datetime.now)
    valid_to = db.Column(db.Date, nullable=True)  # Null = vigente

    created_at = db.Column(db.DateTime, default=datetime.now)

    variant = db.relationship("ProductVariant")


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


class ProductionCheckpoint(db.Model):
    __tablename__ = "production_checkpoints"

    id = db.Column(db.Integer, primary_key=True)
    order_line_id = db.Column(db.Integer, db.ForeignKey("production_order_lines.id"), nullable=False)
    stage = db.Column(db.String(20))  # corte, aparado, armado, terminado
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)


class PlanChangeLog(db.Model):
    __tablename__ = "plan_change_logs"

    id = db.Column(db.Integer, primary_key=True)
    production_order_id = db.Column(db.Integer, db.ForeignKey("production_orders.id"), nullable=False)
    field_changed = db.Column(db.String(50))  # Ej: 'start_date', 'workers_assigned'
    old_value = db.Column(db.String(100))
    new_value = db.Column(db.String(100))
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.today)

    user = db.relationship("User")
    #production_order = db.relationship("ProductionOrder", backref="plan_change_logs")


class ProductionEvent(db.Model):
    __tablename__ = "production_events"

    id = db.Column(db.Integer, primary_key=True)
    production_order_id = db.Column(db.Integer, db.ForeignKey("production_orders.id"), nullable=False)
    event_type = db.Column(db.String(50))  # Ej: 'material_shortage', 'machine_breakdown'
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.today)