from flask import flash

from app import db

from datetime import datetime, date

import pytz

import pandas as pd


guayaquil_tz = pytz.timezone('America/Guayaquil')


def utc_now():
    return datetime.now(pytz.utc).astimezone(guayaquil_tz).strftime('%Y-%m-%d %H:%M:%S')

def get_today():
    date = datetime.today().astimezone(guayaquil_tz).strftime('%Y-%m-%d')
    return date

def update_user_form_choices(field, obj):

    choices = [('', 'Seleccione una opcion')]

    choices += [(c.code, c.name) for c in obj.query.all() if c.code != 'admin']

    field.choices = choices


def process_boom_data(df, expected_columns):
    print(expected_columns)

    
    df.columns = df.columns.str.strip()  # Elimina espacios en blanco
    df.columns = df.columns.str.lower() 

    if not set(expected_columns).issubset(df.columns):
       
        flash(f'El archivo no contiene las columnas correctas. Se esperaban {expected_columns}.', 'danger')
        return {'errors':'No corrcto columns'}
    
 
    
    entries = []
    errors = []

    for _, row in df.iterrows():
        serie_code = row['serie_code']
        material_code = row['material_code']
        unit = row['unit']
        detail = row['detail']
        qty = row['qty']

        error_msg = []

        # Validaciones
        if pd.isna(serie_code) or pd.isna(material_code) or pd.isna(unit) or pd.isna(qty):
            error_msg.append('Campos vacíos')
        
        from ..products.models import MaterialGroup, SizeSeries, Material

        serie = SizeSeries.query.filter_by(name=serie_code).first()

        material = Material.query.filter_by(code=material_code).first()
        
        if serie is None:
            error_msg.append(f'La serie con codigo: {serie_code} no existe')

        if material is None:
            error_msg.append(f'El material con codigo: {material_code} no existe')
        else:
            if material.unit != unit:
                error_msg.append(f'Las unidades no coinciden. Unidades en base de datos {material.unit}. Unidades en archivo: {unit}')
        
        if qty <= 0:
            error_msg.append(f'la cantidad debe ser mayor a 0')

        
        entries.append({
            'serie_code': serie_code,
            'material_code': material_code,
            'detail': material.name if material else "",
            'qty': qty,
            'unit': unit,
            'errors': ', '.join(error_msg)
            })
         

    # Retornar las filas con errores para mostrarlas
    return entries



def process_file_data(df,  objModel, expected_columns):
    print(expected_columns)

    
    df.columns = df.columns.str.strip()  # Elimina espacios en blanco
    df.columns = df.columns.str.lower() 

    if not set(expected_columns).issubset(df.columns):
       
        flash(f'El archivo no contiene las columnas correctas. Se esperaban {expected_columns}.', 'danger')
        return {'errors':'No corrcto columns'}
    
    existing_codes_in_db = {record.code for record in objModel.query.with_entities(objModel.code).all()}
    new_codes = set()
    
    entries = []
    errors = []

    for _, row in df.iterrows():
        code = row['code']
        name = row['name']
        unit = row['unit']
        detail = row['detail']
        group = row['group']

        error_msg = []

        # Validaciones
        if pd.isna(code) or pd.isna(name) or pd.isna(unit) or pd.isna(group) or pd.isna(detail):
            error_msg.append('Campos vacíos')
        
        if code in new_codes:
            error_msg.append(f'Código duplicado en el archivo: {code}.')
        
        if code in existing_codes_in_db:
            error_msg.append(f'Código ya existente en la base de datos: {code}.')
        
        from ..products.models import MaterialGroup

        group_id = MaterialGroup.query.filter_by(code=group).first()

        if error_msg:
            errors.append({
                'code': code,
                'group': group,
                'name': name,
                'detail': detail,
                'unit': unit,
                'errors': ', '.join(error_msg)
            })
        else:
            new_codes.add(code)
            new_entry = objModel(
                code=code,
                name=name,
                detail=detail,
                unit=unit,
                material_group_id=group_id.id
            )
            entries.append(new_entry)

    # Guardar los registros válidos
    db.session.bulk_save_objects(entries)
    db.session.commit()

    # Retornar las filas con errores para mostrarlas
    return {
        'errors': errors,
        'message': f'Se procesaron {len(entries)} registros correctamente, con {len(errors)} errores.'
    }