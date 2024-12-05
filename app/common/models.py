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
