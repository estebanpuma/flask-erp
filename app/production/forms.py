from flask_wtf import FlaskForm
from wtforms import DateField, StringField, IntegerField, SelectField, HiddenField
from wtforms import FormField, FieldList, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Optional

from .validators import validate_model_code, validate_int_qty, validate_scheduled_end_date


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
    delivery_date = DateField('Fecha de entrega', validators=[DataRequired()] )
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


class ProductionRequestForm(FlaskForm):
    class Meta:
        csrf = False
    request_id = HiddenField('ID del Requerimiento')  # Campo oculto para el ID
    is_selected = BooleanField('Seleccionar')  # Checkbox

class ProductionOrderForm(FlaskForm):
    order_number = StringField('Codigo', validators=[DataRequired()])
    scheduled_start_date = DateField('Fecha programada de inicio', validators=[DataRequired()])
    scheduled_end_date = DateField('Fecha programada de fin', validators=[DataRequired(), validate_scheduled_end_date])
    responsible = SelectField('Responsable', choices=[('','Seleccione un opcion')], validators=[DataRequired()])
    notes = TextAreaField('Notes')
    items = FieldList(FormField(ProductionRequestForm), min_entries=0)
    submit = SubmitField('Guardar')

    def __init__(self, *args, **kwargs):
        super(ProductionOrderForm, self).__init__(*args, **kwargs)
        from ..admin.models import User

        for user in User.query.all():
            if user.username != 'admin' and user.is_active:
                self.responsible.choices.append((user.id, user.username ))