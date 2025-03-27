from flask_wtf import FlaskForm

from wtforms import StringField, EmailField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional, Email

from app.common.validations import validate_ruc_or_ci, validate_mobile_phone


class ClientForm(FlaskForm):
    client_type = SelectField(
        'Tipo de Cliente', 
        choices = [('', 'Seleccione una opcion'), ('natural', 'Natural'), ('juridica', 'Juridica')],
        validators=[DataRequired()]
    )
    is_new_client = BooleanField('Nuevo')
    ruc_or_ci = StringField('RUC/CI', validators=[DataRequired(message="Este campo es obligatorio."), validate_ruc_or_ci])
    is_special_taxpayer = BooleanField('Especial', validators=[Optional()])
    #is_ci = BooleanField('CI', validators=[Optional()])
    name = StringField('Nombre', validators=[DataRequired(message="Este campo es obligatorio.")])
    city = StringField('Ciudad', validators=[DataRequired()])
    address = StringField('Direccion', validators=[Optional()])
    phone = StringField('Teléfono', validators=[Optional(), validate_mobile_phone])
    email = EmailField('Email', validators=[Email(message="Ingrese un correo electrónico válido."), Optional()])
    category = SelectField('Categoria', choices=[('', 'Seleccione una categoria')], validators=[Optional()])

    submit = SubmitField('Guardar')


