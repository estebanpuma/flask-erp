from flask_wtf import FlaskForm
from wtforms import FileField
from . validations import validate_massive_file

class MasiveUploadFileForm(FlaskForm):
    file = FileField('Archivo', validators=[validate_massive_file])