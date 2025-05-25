from ..core.exceptions import *


#*******************Products*******************

def validate_product_input(data):
    required = ["code", "name", "variant"]
    for field in required:
        if not data.get(field):
            raise ValidationError(f"El campo {field} es obligatorio.")

    variant = data["variant"]
    for vf in ["size_id", "color_ids", "serie_id", "materials"]:
        if not variant.get(vf):
            raise ValidationError(f"El campo {vf} en la variante es obligatorio.")

    if not isinstance(variant["color_ids"], list) or len(variant["color_ids"]) == 0:
        raise ValidationError("Debes enviar al menos un color.")

    if not isinstance(variant["materials"], list) or len(variant["materials"]) == 0:
        raise ValidationError("La variante debe tener materiales definidos.")
    
def validate_product_patch_data(data, instance):
    if not data:
        raise ValidationError('No se enviaron datos para actualizar.')
    
    
#************************ProductVariant**************************************
#****************************************************************************
def validate_variant_input(data):
    required = ['product_id', 'size_id', 'color_ids']
    for field in required:
        if not data.get(field):
            raise ValidationError(f"El campo {field} es obligatorio.")

    if not isinstance(data['color_ids'], list) or len(data['color_ids']) == 0:
        raise ValidationError("Debes enviar al menos un color.")

def validate_variant_patch(data, instance):
    if "size_id" in data and data["size_id"] != instance.size_id:
        raise ValidationError("No puedes cambiar la talla una vez creada la variante.")

    if "product_id" in data and data["product_id"] != instance.product_id:
        raise ValidationError("La variante no puede cambiar de producto.")

    if "color_ids" in data:
        if not isinstance(data["color_ids"], list) or len(data["color_ids"]) == 0:
            raise ValidationError("Debes enviar al menos un color.")


    

#*****************************ProdctVariantMaterials*****************
def validate_product_variant_materials_input(data):
    required = ['variant_id', 'material_id', 'serie_id', 'quantity']
    for field in required:
        if not data.get(field):
            raise ValidationError(f"El campo {field} es obligatorio.")
        
    if "quantity" in data and (not isinstance(data["quantity"], (int, float)) or data["quantity"] <= 0):
        raise ValidationError("La cantidad debe ser un número mayor a 0.")

    
    
#****************************Series*************************

def validate_size_series_update(data, instance):
    if not data:
        raise ValidationError("No se enviaron datos.")

    allowed = {"name", "description", "start_size", "end_size"}
    for key in data:
        if key not in allowed:
            raise ValidationError(f"Campo no permitido: {key}")

    if 'name' in data and not str(data['name']).strip():
        raise ValidationError("El campo 'name' no puede estar vacío.")

    if 'start_size' in data and not isinstance(data['start_size'], (int, float)):
        raise ValidationError("El campo 'start_size' debe ser un número.")
    if 'end_size' in data and not isinstance(data['end_size'], (int, float)):
        raise ValidationError("El campo 'end_size' debe ser un número.")

    # ✅ VALIDACIÓN CLAVE: end_size >= start_size
    new_start = data.get('start_size', instance.start_size)
    new_end = data.get('end_size', instance.end_size)
    if new_end < new_start:
        raise ValidationError("La talla final no puede ser menor que la talla inicial.")
        

def validate_size_series_create(data):
    errors = {}
    from .services import SeriesService
    if SeriesService._get_series_by_name(data.get('name')):
        raise ValidationError('Ya existe una serie con ese nombre')
    if not data.get('name'):
        errors['name'] = 'El nombre es obligatorio'
    if 'start_size' not in data:
        errors['start_size'] = 'Debe especificar una talla inicial'
        raise ValidationError('Debe especificar una talla inicial')
    if 'end_size' not in data:
        errors['end_size'] = 'Debe especificar una talla final'
    elif data['end_size'] < data['start_size']:
        errors['end_size'] = 'La talla final no puede ser menor que la inicial'
        raise ValidationError('La talla final no puede ser menor que la inicial')
    return errors


def validate_size_create(data):
    errors = {}
    if not data.get('value'):
        errors['value'] = 'El valor de la talla es obligatorio'
    if 'series_id' not in data:
        errors['series_id'] = 'Debe especificar una serie'
    return errors

def validate_size_update(data):
    # PATCH permite campos parciales
    if not data:
        return {'general': 'Debe enviar al menos un campo a actualizar'}
    return {}





##*********************** Materials **********************************************

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
    

#********************************* COlor**********************************

def validate_color_input(data):
    required_fields = ['name', 'code']
    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"El campo {field} es obligatorio.")

def validate_color_patch(data, instance):
    if not data:
        raise ValidationError('No se enviaron datos para actualizar.')