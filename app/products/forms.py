from flask_wtf import FlaskForm

from wtforms import  IntegerField, StringField, SubmitField, MultipleFileField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Optional

from .models import ProductSubLine, ProductLine


class ProductModelForm(FlaskForm):

    line = SelectField('Linea', validators=[DataRequired()], choices=[('', 'Seleccione una linea')])
    subline = SelectField('Sublinea', validators=[Optional()], choices=[('', 'Seleccione una linea')])
    code = StringField('Codigo', validators=[DataRequired()])
    name = StringField('Nombre', validators=[DataRequired()])
    description = TextAreaField('Descripcion', validators=[Optional()])
    images = MultipleFileField('Imagenes', validators={Optional()})
    submit = SubmitField('Guardar')

    def __init__(self, *args, **kwargs):
        super(ProductModelForm, self).__init__(*args, **kwargs)
        for line in ProductLine.query.all():
            self.line.choices.append((line.id, f'{line.code}-{line.name}'))
        for subline in ProductSubLine.query.all():
            self.subline.choices.append((subline.id, f'{subline.code}-{subline.name}'))
            


class ProductLineForm(FlaskForm):

    code = StringField('Codigo', validators=[DataRequired()])
    name = StringField('Nombre', validators=[DataRequired()])
    description = TextAreaField('Descripcion', validators=[Optional()])
    submit = SubmitField('Guardar')

class ProductSubLineForm(FlaskForm):

    code = StringField('Codigo', validators=[DataRequired()])
    name = StringField('Nombre', validators=[DataRequired()])
    description = TextAreaField('Descripcion', validators=[Optional()])
    submit = SubmitField('Guardar')