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


def process_file_data(df,  objModel, expected_columns):
    print(expected_columns)

    
    df.columns = df.columns.str.strip()  # Elimina espacios en blanco
    df.columns = df.columns.str.lower() 

    if not set(expected_columns).issubset(df.columns):
       
        flash(f'El archivo no contiene las columnas correctas. Se esperaban {expected_columns}.', 'danger')
        return ['No corrcto columns']
    
    existing_codes_in_db = {record.code for record in objModel.query.with_entities(objModel.code).all()}
    new_codes = set()
    
    entries = []
    errors = []

    for _, row in df.iterrows():
        code = row['code']
        name = row['name']
        unit = row['unit']

        error_msg = []

        # Validaciones
        if pd.isna(code) or pd.isna(name) or pd.isna(unit):
            error_msg.append('Campos vacíos: name o unit.')
        
        if code in new_codes:
            error_msg.append(f'Código duplicado en el archivo: {code}.')
        
        if code in existing_codes_in_db:
            error_msg.append(f'Código ya existente en la base de datos: {code}.')

        if error_msg:
            errors.append({
                'code': code,
                'name': name,
                'description': row.get('description', ''),
                'unit': unit,
                'errors': ', '.join(error_msg)
            })
        else:
            new_codes.add(code)
            new_entry = objModel(
                code=code,
                name=name,
                description=row['description'],
                unit=unit
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