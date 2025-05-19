from ..core.exceptions import *


#********************Material***********************

def validate_material_data(data):
    errors = {}
    if not data.get('code'):
        errors['code'] = 'El código es obligatorio.'
    if not data.get('name'):
        errors['name'] = 'El nombre es obligatorio.'
    if not data.get('unit'):
        errors['unit'] = 'La unidad es obligatoria.'
    if errors:
        raise ValidationError(errors)


def validate_material_patch_data(data, instance):
    if not data:
        raise ValidationError('No se enviaron datos para actualizar.')
    

#********************MaterialGroup***********************
def validate_material_group_data(data):
    errors = {}
    if not data.get('code'):
        errors['code'] = 'El código es obligatorio.'
    if not data.get('name'):
        errors['name'] = 'El nombre es obligatorio.'
    if errors:
        raise ValidationError(errors)


def validate_material_group_patch_data(data, instance):
    if not data:
        raise ValidationError('No se enviaron datos para actualizar.')