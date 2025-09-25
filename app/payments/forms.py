from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class PaymentMethodForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    description = StringField()
    submit = SubmitField()
