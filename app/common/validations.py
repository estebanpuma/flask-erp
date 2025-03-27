from wtforms.validators import ValidationError

from werkzeug.security import check_password_hash


def no_admin(form, field):
    if 'admin' in field.data.lower():
        raise ValidationError('El nombre de usuario no puede contener "admin".')


def validate_ci(form, field):
    cedula = field.data
    if not cedula.isdigit():
        raise ValidationError('La cédula debe contener solo números.')
    if len(cedula) != 10:
        raise ValidationError('La cédula debe tener exactamente 10 dígitos.')
    from ..admin.models import User
    if User.query.filter(User.ci==cedula).first():
        raise ValidationError('El numero de cedula ya esta registrado')
    

def validate_mobile_phone(form, field):
    phone = field.data
    if not phone.isdigit():
        raise ValidationError('Numero celular contener solo números.')
    if len(phone) != 10:
        raise ValidationError('El número debe tener exactamente 10 dígitos.')
    

def validate_username(form, field):
    username = field.data
    if len(username) < 3:
        raise ValidationError('El nombre debe tener al menos 3 caracteres')
    

def validate_login_email(form, field):
    user_email = field.data
    from ..admin import User
    user = User.query.filter_by(email = user_email).first()
    if user is None:
        raise ValidationError('Email no existe, por favor ingrese un email correcto')
    

def validate_login_password(form, field):
    user_email = form.email.data
    from ..admin import User
    user = User.query.filter_by(email = user_email).first()
    user_password = field.data
    if user:
        if not user.check_password(user_password):
            raise ValidationError('Password incorrecto')
        

def validate_ruc_or_ci(form, field):
    ruc_or_ci = field.data

    if not ruc_or_ci.isdigit():
        raise ValidationError('El RUC/CI debe contener solo números.')
    
    if len(ruc_or_ci) != 13 and len(ruc_or_ci) !=10 :
        raise ValidationError('El campo debe tener 10 digitos si es cedula o 13 dígitos si es RUC')
    
        
def validate_massive_file(form, field):
    file = field.data
    file_extension = file.filename.split('.')[-1]
    if file_extension not in ['csv', 'xlsx']:
        raise ValidationError('El archivo no tiene el formato requerido')
    

def validate_material_code(form, field):
    code = field.data
    
    from ..inventory.services import MaterialServices
    material = MaterialServices.get_material_by_code(code)
    if material is None:
        raise ValidationError('El codigo no existe')
    
def validate_scheduled_end_date(form, field):
    if field.data <= form.scheduled_start_date.data:
        raise ValidationError('La fecha de fin debe ser posterior a la de inicio.')


def validate_existing_line_code(form, field):
    code = field.data
    
    from ..products.services import LineServices
    line=None
    if line  is None:
        raise ValidationError('El codigo ya existe')
    
    
def validate_existing_color_code(form, field):
    code = field.data

    from ..products.services import ColorServices
    color = ColorServices.get_color_by_code(code)
    if color is not None:
        raise ValidationError('El codigo ya existe')
    

def validate_size_value(form, field):
    value = field.data
    
    from ..products.services import SeriesServices
    all_sizes = SeriesServices.get_all_sizes()

    for size in all_sizes:
        if value == int(size.value):
            # Obtenemos la serie para informar al usuario en cuál serie existe la talla
            serie = SeriesServices.get_serie(size.series_id)
            raise ValidationError(f'La talla ya existe en la serie {serie.name}')
            

def validate_serie_name(form, field):
    name = field.data
    from ..products.models import SizeSeries
    serie = SizeSeries.query.filter_by(name=name).first()
   
    if serie:
        # Obtenemos la serie para informar al usuario en cuál serie existe la talla
        raise ValidationError(f'Nombre de serie ya existe')