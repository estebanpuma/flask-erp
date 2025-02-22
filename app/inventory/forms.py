from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, IntegerField, SubmitField, DateField, FloatField, FieldList, FormField, SelectField, HiddenField
from wtforms.validators import DataRequired, Optional
from .models import Warehouse
from ..common.validations import validate_material_code



#################################################################################
#********************************BASEFORM***************************************
#********************************************************************************

#Creo un Subformulario base tipo FieldList para los items del movimiento de inventario
class MovementItemsList(FlaskForm):
    class Meta:
        csrf = False
    code = StringField('Codigo', validators=[DataRequired(message='Campo requerido')])
    material = StringField('Nombre', validators=[DataRequired(message='Campo requerido')])
    unit = StringField('Unidad', validators=[DataRequired(message='Campo requerido')])
    qty = FloatField('Cantidad', validators=[DataRequired(message='Campo requerido')])

#Heredo del subformulario principal (MovementItemsList) para ralizar la validacon del codigo
# en funcion del tipo de item
class MaterialList(MovementItemsList):
    code = StringField('Codigo', validators=[DataRequired(message='Campo requerido'), validate_material_code])


class ProductList(MovementItemsList):
    code = StringField('Codigo', validators=[DataRequired(message='Campo requerido')])


class ToolList(MovementItemsList):
    code = StringField('Codigo', validators=[DataRequired(message='Campo requerido')])


class WIPList(MovementItemsList):
    code = StringField('Codigo', validators=[DataRequired(message='Campo requerido')])


#Creo el formulario principal para registar movimientos de inventario
class InventoryMovementForm(FlaskForm):
    date = DateField('Fecha', validators=[DataRequired(message='Campo requerido')])
    movement_trigger = SelectField('Tipo', choices=[('', 'Seleccione')])
    warehouse = SelectField('Bodega', choices=[('', 'Seleccione')], validators=[DataRequired(message='Campo requerido')])
    responsible = SelectField('Responsable', choices=[('', 'Seleccione una opcion')],validators=[DataRequired(message='Campo requerido')])
    document = StringField('N.Documento', validators=[DataRequired(message='Campo requerido')])
    
    submit = SubmitField('Guardar')

    def __init__(self, *args, **kwargs):
        super(InventoryMovementForm, self).__init__(*args, **kwargs)

        from ..admin.models import User

        for user in User.query.all():
            if user.username != 'admin' and user.is_active:
                self.responsible.choices.append((user.id, user.username ))

        for wh in Warehouse.query.all():
            self.warehouse.choices.append((wh.id, wh.name))


#Heredo del formulario principal(InventoryMovementForm) para crear movimientos de inventario segun el tipo y el item
#los tipos pueden ser ingreso y egreso(Entry, Exit). Los items (por el momento) Material, Product, WIP, Tools

#Materials
class MaterialEntryForm(InventoryMovementForm):
    movement_trigger = SelectField('Motivo', validators=[DataRequired(message='Campo requerido')],
                            choices=[('','Seleccione'), 
                                     ('PURCHASE', 'Compra'),
                                     ('REENTRY', 'Ajuste'),
                                     ('ROTATION', 'Rotacion')])
    items = FieldList(FormField(MaterialList), min_entries=0)#cargo el subformulario


class MaterialExitForm(InventoryMovementForm):
    movement_trigger = SelectField('Motivo', validators=[DataRequired(message='Campo requerido')],
                            choices=[('','Seleccione'), 
                                     ('PRODUCTION', 'Produccion'),
                                     ('ADJUST', 'Ajuste'),
                                     ('ROTATION', 'Rotacion'),
                                     ('REMOVE', 'Baja')])
    items = FieldList(FormField(MaterialList), min_entries=0)#cargo el subformulario


#Products
class ProductEntryForm(InventoryMovementForm):
    items = FieldList(FormField(ProductList), min_entries=0)#cargo el subformulario
    movement_trigger = SelectField('Motivo', validators=[DataRequired(message='Campo requerido')],
                            choices=[('','Seleccione'), 
                                     ('PRODUCTION', 'Produccion'),
                                     ('ROTATION', 'Rotacion')])


class ProductExitForm(InventoryMovementForm):
    items = FieldList(FormField(ProductList), min_entries=0)#cargo el subformulario
    movement_trigger = SelectField('Motivo', validators=[DataRequired(message='Campo requerido')],
                            choices=[('','Seleccione'), 
                                     ('SALES', 'Ventas'),
                                     ('ROTATION', 'Rotacion'),
                                     ('REMOVE', 'Baja')])





#***********************
class MaterialGroupForm(FlaskForm):
    code = StringField('Codigo', validators=[DataRequired()])
    name = StringField('Nombre', validators=[DataRequired()])
    description = StringField('Descripcion', validators=[Optional()])
    submit = SubmitField('Guardar')
    

class MaterialForm(FlaskForm):

    code = StringField('Codigo', validators=[DataRequired()])
    group = SelectField('Grupo', validators=[DataRequired()], choices=[('', 'Seleccione')])
    name = StringField('Nombre', validators=[DataRequired()])
    detail = StringField('Detalle', validators=[Optional()])
    unit = StringField('Unidad', validators=[DataRequired()])
    price = FloatField('Precio', validators=[DataRequired()])
    submit = SubmitField('Guardar')

    def __init__(self, *args, **kwargs):
        super(MaterialForm, self).__init__(*args, **kwargs)

        from .services import MaterialGroupServices
        groups = MaterialGroupServices.get_all_material_groups()

        for group in groups:
            self.group.choices.append((group.id, f'{group.code}-{group.name}' ))


class WarehouseForm(FlaskForm):
    code = StringField('Codigo', validators=[DataRequired()])
    name = StringField('Nombre', validators=[DataRequired()])
    description = StringField('Descripcion', validators=[Optional()])
    location = StringField('Ubicacion', validators=[DataRequired()])
    submit = SubmitField('Guardar')