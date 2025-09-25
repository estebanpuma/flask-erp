from app import db

from ..common import SoftDeleteMixin


class GrossMargin(db.Model, SoftDeleteMixin):

    __tablename__ = "gross_margins"

    id = db.Column(db.Integer, primary_key=True)
    # % percentage
    value = db.Column(db.Float, nullable=False)
    begin_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active_margin = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<GrossMargin(value={self.value}, begin_date={self.begin_date}, end_date={self.end_date})>"
