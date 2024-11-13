from flask_wtf import FlaskForm
from wtforms import DateField, StringField, IntegerField, SelectField, FormField, FieldList
from wtforms.validators import DataRequired, Optional


class StockOrderProducts(FlaskForm):
    class Meta:
        csrf = False
    code = StringField('Codigo', validators=[DataRequired()])
    size = IntegerField('Talla', validators=[DataRequired()])
    qty = IntegerField('Cantidad', validators=[DataRequired()])
    notes = StringField('Notas', validators=[Optional()])


class StockOrderForm(FlaskForm):
    code = StringField('Codigo', validators=[DataRequired()])
    request_date = DateField('Fecha de pedido', validators=[DataRequired()] )
    responsible = SelectField('Responsable', choices=[('','Seleccione un opcion')], validators=[DataRequired()])
    notes = StringField('Notas', validators=[Optional()])
    products = FieldList(FormField(StockOrderProducts), min_entries=0)

    def __init__(self, *args, **kwargs):
        super(StockOrderForm, self).__init__(*args, **kwargs)
        from ..admin.models import User

        for user in User.query.all():
            if user.username != 'admin' and user.is_active:
                self.responsible.choices.append((user.id, user.username ))