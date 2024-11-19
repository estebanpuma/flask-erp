from flask_wtf import FlaskForm
from wtforms import DateField, StringField, IntegerField, SelectField, FormField, FieldList, SubmitField
from wtforms.validators import DataRequired, Optional

from .validators import validate_model_code, validate_int_qty


class StockOrderProducts(FlaskForm):
    class Meta:
        csrf = False
    code = StringField('Codigo', validators=[DataRequired(), validate_model_code])
    size = IntegerField('Talla', validators=[DataRequired()])
    qty = IntegerField('Cantidad', validators=[DataRequired(), validate_int_qty])
    notes = StringField('Notas', validators=[Optional()])


class StockOrderForm(FlaskForm):
    code = StringField('Codigo', validators=[DataRequired()])
    request_date = DateField('Fecha de pedido', validators=[DataRequired()] )
    responsible = SelectField('Responsable', choices=[('','Seleccione un opcion')], validators=[DataRequired()])
    notes = StringField('Notas', validators=[Optional()])
    items = FieldList(FormField(StockOrderProducts), min_entries=1)
    submit = SubmitField('Guardar')

    def __init__(self, *args, **kwargs):
        super(StockOrderForm, self).__init__(*args, **kwargs)
        from ..admin.models import User

        for user in User.query.all():
            if user.username != 'admin' and user.is_active:
                self.responsible.choices.append((user.id, user.username ))