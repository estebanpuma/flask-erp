from datetime import datetime

import pandas as pd
import pytz

from app import db

from ..core.exceptions import ValidationError

# utils/excel_import_service.py


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


guayaquil_tz = pytz.timezone("America/Guayaquil")


def utc_now():
    return datetime.now(pytz.utc).astimezone(guayaquil_tz).strftime("%Y-%m-%d %H:%M:%S")


def get_today():
    date = datetime.today().astimezone(guayaquil_tz).strftime("%Y-%m-%d")
    return date


def validate_foreign_key(model, obj_id, field_name="ID"):
    instance = model.query.get(obj_id)
    if not instance:
        raise ValidationError(f"{field_name} {obj_id} no existe.")
    return instance


def get_next_sequence_number(sequence_key: str) -> int:
    """
    Obtiene y autoincrementa un número de secuencia en la base de datos.
    Esta operación DEBE ser parte de la transacción principal que guarda la orden.
    """
    # (El código de esta función es el mismo que te di antes)
    # Asegúrate de que setting.value = str(next_value) y setting se añade/actualiza
    # en la sesión, pero el COMMIT se hace FUERA de esta función.
    from ..common.models import AppSetting

    # Simulación de lectura/escritura en AppSetting

    setting = AppSetting.query.filter(AppSetting.key == sequence_key).first()

    if not setting:
        setting = AppSetting(key=sequence_key, value="0")
        db.session.add(setting)
        # self.db_session.flush() # Importante si necesitas el ID antes del commit

    current_value = int(setting.value)
    next_value = current_value + 1
    setting.value = str(next_value)

    # OJO: NO HAGA commit aquí. El commit lo hace la función que crea la orden.
    return next_value
