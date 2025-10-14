from enum import StrEnum

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum

from app import db

from .utils import utc_now


class LifecycleStatus(StrEnum):
    DRAFT = "DRAFT"
    READY = "READY"
    ARCHIVED = "ARCHIVED"


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)


class SoftDeleteMixin:
    __abstract__ = True

    is_active = db.Column(db.Boolean, default=True)

    lifecycle_status = Column(
        SAEnum(
            LifecycleStatus,
            name="lifecycle_status_enum",  # nombre de tipo claro y único
            native_enum=False,
        ),
        nullable=True,
        server_default=LifecycleStatus.DRAFT.value,
        index=True,
    )


class AppSetting(db.Model):
    __tablename__ = "app_settings"
    key = db.Column(db.String(50), primary_key=True)  # Ej: 'max_overtime_per_day'
    value = db.Column(db.String(255), nullable=False)  # Ej: '4.0'
    name = db.Column(
        db.String(100), nullable=True
    )  # <Ej: 'Horas extras máximas por trabajador'
    description = db.Column(db.String(255), nullable=True)
