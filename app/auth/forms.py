from flask_wtf import FlaskForm

from wtforms import SubmitField, EmailField, PasswordField, StringField, DateField, SelectField, BooleanField

from wtforms.validators import Email, DataRequired

from ..common.validations import validate_login_password, validate_login_email




class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[Email(message="Ingrese un correo electrónico válido."), DataRequired(message="Este campo es obligatorio."), validate_login_email])
    password = PasswordField('Password', validators=[DataRequired(message="Este campo es obligatorio."), validate_login_password])
    remember_me = BooleanField('Recuerdame')
    submit = SubmitField('Login')



