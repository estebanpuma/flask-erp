from app import db
from .models import AppSetting
from sqlalchemy.exc import IntegrityError

class AppSettingService:

    @staticmethod
    def get_next_product_code(letter: str) -> str:
        key = f'PRODUCT_CODE_{letter}'
        setting = AppSetting.query.with_for_update().filter_by(key=key).first()

        if not setting:
            # Si no existe, se crea
            setting = AppSetting(key=key, value='001')
            db.session.add(setting)
            db.session.flush()
            return f"{letter}001"

        next_number = int(setting.value) + 1

        if next_number > 999:
            raise ValueError(f"Se alcanzó el límite de códigos para la letra {letter}")

        setting.value = f"{next_number:03d}"
        
        return f"{letter}{next_number:03d}"

    @staticmethod
    def view_next_product_code(letter: str) -> str:
        key = f'PRODUCT_CODE_{letter}'
        setting = AppSetting.query.with_for_update().filter_by(key=key).first()

        if not setting:
            # Si no existe, se crea
            setting = AppSetting(key=key, value='001')
            return f"{letter}001"

        next_number = int(setting.value) + 1

        if next_number > 999:
            raise ValueError(f"Se alcanzó el límite de códigos para la letra {letter}")

        setting.value = f"{next_number:03d}"
        
        return f"{letter}{next_number:03d}"