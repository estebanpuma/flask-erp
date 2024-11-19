from wtforms.validators import ValidationError


def validate_model_code(form, field):
    code = field.data
    from ..products.services import ProductServices
    material = ProductServices.get_product_by_code(code)
    if material is None:
        raise ValidationError('El codigo no existe')
    
def validate_int_qty(form, field):
    qty = field.data
    if qty <= 0:
        raise ValidationError('La cantidad debe ser mayor a 0')