from flask_wtf import FlaskForm

from wtforms import FormField, FieldList, IntegerField, StringField, SubmitField, MultipleFileField, SelectField, TextAreaField, FloatField, FileField
from wtforms.validators import DataRequired, Optional

from .models import ProductSubLine, ProductLine
from .services import ColorServices

from ..common.validations import validate_existing_line_code, validate_existing_color_code, validate_size_value, validate_serie_name

#Creo un Subformulario base tipo FieldList para los items de la explosion de materiales
class MaterialList(FlaskForm):
    class Meta:
        csrf = False
    serie = StringField('Serie', validators=[DataRequired(message='Campo requerido')])
    detail = StringField('Detalle', validators=[Optional()])
    unit = StringField('Unidad', validators=[Optional()])
    code = StringField('Codigo', validators=[DataRequired(message='Campo requerido')])
    qty = FloatField('Cantidad', validators=[DataRequired(message='Campo requerido')])


class ProductModelForm(FlaskForm):

    line_id = SelectField('Linea', validators=[DataRequired(message='Campo requerido')], choices=[('', 'Seleccione una linea')])
    subline_id = SelectField('Sublinea', validators=[Optional()], choices=[('', 'Seleccione una sublinea')])
    color = SelectField('Color', validators=[DataRequired(message='Campo requerido')], choices=[('', 'Seleccione un color')])
    code = StringField('Codigo', validators=[DataRequired(message='Campo requerido')])
    description = TextAreaField('Descripcion', validators=[Optional()])
    images = MultipleFileField('Imagenes', validators={Optional()})
    #file = FileField('Archivo', validators=[Optional()])
    items = FieldList(FormField(MaterialList), min_entries=0)
    submit = SubmitField('Guardar')

    def __init__(self, *args, **kwargs):
        super(ProductModelForm, self).__init__(*args, **kwargs)
        for line in ProductLine.query.all():
            self.line_id.choices.append((line.id, f'{line.code}-{line.name}'))
        for subline in ProductSubLine.query.all():
            self.subline_id.choices.append((subline.id, f'{subline.code}-{subline.name}'))
        for color in ColorServices.get_all_colors():
            self.color.choices.append((color.id, f'{color.code}-{color.name}'))
            


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


class ColorForm(FlaskForm):

    code = StringField('Codigo', validators=[DataRequired(), validate_existing_color_code])
    name = StringField('Nombre', validators=[DataRequired()])
    hex = StringField('Hex', validators=[Optional()])
    description = TextAreaField('Descripcion', validators=[Optional()])
    submit = SubmitField('Guardar')


class SerieForm(FlaskForm):

    name = StringField('Nombre', validators=[DataRequired(), validate_serie_name])
    description = TextAreaField('Descripcion', validators=[Optional()])
    start_size = IntegerField('T. Inical', validators=[DataRequired()])
    end_size = IntegerField('T. FInal', validators=[DataRequired()])
    submit = SubmitField('Guardar')