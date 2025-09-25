from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired


class GrossMarginForm(FlaskForm):
    value = FloatField("Valor", validators=[DataRequired(message="Ingrese un valor")])
    notes = StringField("Notas")
    submit = SubmitField("Guardar")
