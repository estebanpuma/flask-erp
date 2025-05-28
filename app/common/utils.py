from datetime import datetime, date

import pytz

import pandas as pd

# utils/excel_import_service.py

import pandas as pd
from ..core.exceptions import ValidationError


class ExcelImportService:
    required_columns = []  # debe ser definido por subclase

    @classmethod
    def read_excel(cls, file):
        try:
            df = pd.read_excel(file, engine="openpyxl")
        except Exception:
            raise ValidationError("No se pudo leer el archivo Excel.")

        missing = [col for col in cls.required_columns if col not in df.columns]
        if missing:
            raise ValidationError(f"Faltan columnas obligatorias: {missing}")

        return df

    @classmethod
    def process(cls, file, row_handler):
        """
        file: archivo tipo FileStorage de Flask (request.files["file"])
        row_handler: función que recibe un dict por fila y retorna True/False
        """
        df = cls.read_excel(file)
        results = []
        for idx, row in df.iterrows():
            data = row.to_dict()
            try:
                row_handler(data)
                results.append({**data, "status": "ok"})
            except Exception as e:
                results.append({**data, "status": "error", "error": str(e)})

            from app import db
            if any(r.get("status") == "ok" for r in results):
                db.session.commit()
                
        return results



guayaquil_tz = pytz.timezone('America/Guayaquil')


def utc_now():
    return datetime.now(pytz.utc).astimezone(guayaquil_tz).strftime('%Y-%m-%d %H:%M:%S')

def get_today():
    date = datetime.today().astimezone(guayaquil_tz).strftime('%Y-%m-%d')
    return date



def validate_foreign_key(model, obj_id, field_name="ID"):
    instance = model.query.get(obj_id)
    if not instance:
        raise ValidationError(f"{field_name} {obj_id} no existe.")
    return instance