from ..common import BaseModel

from app import db

from datetime import date as dt

class RDOrder(BaseModel):
    __tablename__ = "rd_orders"

    id = db.Column(db.Integer, primary_key=True)
    objective = db.Column(db.String(150))
    hypothesis = db.Column(db.Text)
    expected_feedback_date = db.Column(db.Date)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    created_by = db.relationship("User")
