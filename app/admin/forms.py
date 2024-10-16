from flask_wtf import FlaskForm

from wtforms import StringField, EmailField, PasswordField, SelectField, BooleanField, SubmitField, TextAreaField, FieldList, FormField, SelectFieldBase
from wtforms.validators import Email, DataRequired, Optional

from .models import Role

from app.common.validations import no_admin, validate_ci, validate_username


class SignupForm(FlaskForm):
    ci = StringField('Cédula', validators=[DataRequired(message="Este campo es obligatorio."), validate_ci])
    username = StringField('Nombre', validators=[DataRequired(message="Este campo es obligatorio."), no_admin, validate_username])
    email = EmailField('Email', validators=[Email(message="Ingrese un correo electrónico válido."), DataRequired(message="Este campo es obligatorio.")])
    password = PasswordField('Password', validators=[DataRequired(message="Este campo es obligatorio.")])
    #confirm_password = PasswordField('Password', validators=[DataRequired()])
    job = SelectField('Cargo', choices=[('', 'Seleccione un cargo')])
    submit = SubmitField('Registrar')

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.job.choices += [(c.code, c.name) for c in Role.query.all() if c.code != 'admin']


class UpdateUserForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.password.validators = [Optional()]


class JobForm(FlaskForm):
    code = StringField('Codigo', validators=[DataRequired(message="Este campo es obligatorio.")])
    name = StringField('Cargo', validators=[DataRequired(message="Este campo es obligatorio.")])
    description = TextAreaField('Descripción')
    submit = SubmitField('Guardar')


class RoleForm(FlaskForm):
    code = StringField('Codigo', validators=[DataRequired(message="Este campo es obligatorio.")])
    name = StringField('Rol', validators=[DataRequired(message="Este campo es obligatorio.")])
    description = TextAreaField('Descripción')
    submit = SubmitField('Guardar')



class SelectRolesForm(FlaskForm):
    role_name = StringField()  # Campo para mostrar el nombre del rol
    assign = BooleanField()  # Campo booleano para asignar el rol

class AssignRolesForm(FlaskForm):
    #roles = FieldList(FormField(SelectRolesForm))  # FieldList de formularios para roles
    submit = SubmitField('Guardar')

    #def __init__(self, user=None, *args, **kwargs):
     #   super(AssignRolesForm, self).__init__(*args, **kwargs)

        