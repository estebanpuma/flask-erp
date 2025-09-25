from app import db

from .utils import utc_now


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)


class SoftDeleteMixin:
    __abstract__ = True

    is_active = db.Column(db.Boolean, default=True)


class AppSetting(db.Model):
    __tablename__ = "app_settings"
    key = db.Column(db.String(50), primary_key=True)  # Ej: 'max_overtime_per_day'
    value = db.Column(db.String(255), nullable=False)  # Ej: '4.0'
    name = db.Column(
        db.String(100), nullable=True
    )  # <Ej: 'Horas extras máximas por trabajador'
    description = db.Column(db.String(255), nullable=True)
