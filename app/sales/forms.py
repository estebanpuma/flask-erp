from flask_wtf import FlaskForm
from wtforms.validators import Email, DataRequired
from wtforms import StringField, IntegerField, SubmitField, DateField, SelectField, FormField, FieldList, FloatField
from ..admin.services import AdminServices
from ..payments.services import PaymentMethodService

from ..crm.forms import ClientForm

class GeneralOrderInfoForm(FlaskForm):
    order_number = IntegerField('Orden', validators=[DataRequired()])
    request_date = DateField('Fecha de pedido',format='%Y-%m-%d', validators=[DataRequired()])
    delivery_date = DateField('Fecha de entrega',format='%Y-%m-%d', validators=[DataRequired()])
    salesperson = SelectField('Vendedor', validators=[DataRequired()], choices=[])
    submit = SubmitField('Siguiente')

    def __init__(self, *args, **kwargs):
            super(GeneralOrderInfoForm, self).__init__(*args, **kwargs)
            self.salesperson.choices += [(c.id, c.username) for c in AdminServices.get_users_by_type('salesperson') ]


class SelectedSizes(FlaskForm):
    class Meta:
        csrf = False
    size = IntegerField(validators=[DataRequired()])
    qty = IntegerField(validators=[DataRequired()])


class SelectedModelForm(FlaskForm):
    class Meta:
        csrf = False
    model = StringField(validators=[DataRequired()])
    sizes = FieldList(FormField(SelectedSizes), min_entries=1)


class ProductOrderForm(FlaskForm):
    order = FieldList(FormField(SelectedModelForm), min_entries=1)
    total_items = IntegerField(validators=[DataRequired()])
    total_amount = FloatField(validators=[DataRequired()])
    submit = SubmitField()


class InstallementForm(FlaskForm):
    class Meta:
        csrf = False
    n_installement = IntegerField(validators=[DataRequired()])
    payment_date = DateField(validators=[DataRequired()])
    amount = FloatField(validators=[DataRequired()])


class PaymentForm(FlaskForm):
     payment_method = SelectField(validators=[DataRequired()], choices=[('', 'Seleccione un metodo')])
     n_installements = IntegerField(validators=[DataRequired()])
     installements = FieldList(FormField(InstallementForm), min_entries=1)
     total_amount = FloatField()
     submit = SubmitField()

     def __init__(self, *args, **kwargs):
          super(PaymentForm, self).__init__(*args, **kwargs)
          self.payment_method.choices += [(c.id, c.name) for c in PaymentMethodService.get_all_payment_methods()]


class CheckoutForm(FlaskForm):
     submit = SubmitField()