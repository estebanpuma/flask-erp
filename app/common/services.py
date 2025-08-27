from app import db
from .models import AppSetting
from sqlalchemy.exc import IntegrityError
    

class ProductCodeGenerator:

    @staticmethod
    def get_model_counter_key(linea, sublinea, tipo, coleccion):
        codigo = linea.code
        if sublinea:
            codigo += sublinea.code
        codigo += tipo.code
        codigo += str(coleccion.code)
        return str(codigo).upper()

    @staticmethod
    def get_next_model_code(linea, sublinea, tipo, coleccion):
        key = ProductCodeGenerator.get_model_counter_key(linea, sublinea, tipo, coleccion)
        app_settings_key = f'product_counter_{key}'
        setting = AppSetting.query.filter_by(key=app_settings_key).first()
        if not setting:
            setting = AppSetting(key=app_settings_key, value='1')
            db.session.add(setting)
            db.session.flush()
            return f'{key}001'
        else:
            current = int(setting.value)
            setting.value = str(current + 1)
            db.session.flush()
            next_num = current + 1
            next_code = f"{key}{next_num:03d}"
            return next_code

    @staticmethod
    def preview_model_code(linea, sublinea, tipo, coleccion):
        """Obtiene el número actual sin incrementarlo."""
        key = ProductCodeGenerator.get_model_counter_key(linea, sublinea, tipo, coleccion)
        app_settings_key = f'product_counter_{key}'
        setting = AppSetting.query.filter_by(key=app_settings_key).first()
        if not setting:
            return f'{key}001'
        else: 
            next_num = int(setting.value) + 1
            next_code = f"{key}{next_num:03d}"
            return next_code  


    @staticmethod
    def _build_prefix(linea, sublinea, tipo, coleccion_id):
        """Reutilizable para preview y generación final."""
        prefix = linea.code
        if sublinea:
            prefix += sublinea.code
        prefix += tipo.code
        prefix += str(coleccion_id)
        return prefix


class CollectionCodeGenerator:

    @staticmethod
    def get_counter_key(linea, sublinea, tipo):
        key = linea.code
        if sublinea:
            key += sublinea.code
        
        key += tipo.code
        return f"collection_counter_{key}"

    @staticmethod
    def get_next_collection_number(linea, sublinea, tipo):
        key = CollectionCodeGenerator.get_counter_key(linea, sublinea, tipo)
        setting = AppSetting.query.filter_by(key=key).first()

        if not setting:
            setting = AppSetting(key=key, value='1')
            db.session.add(setting)
            db.session.flush()
            return 1
        else:
            current = int(setting.value)
            setting.value = str(current + 1)
            db.session.flush()
            return current + 1
        
    @staticmethod
    def preview_collection_number(linea, sublinea, tipo) -> int:
        key = CollectionCodeGenerator.get_counter_key(linea, sublinea, tipo)
        setting = AppSetting.query.filter_by(key=key).first()
        return int(setting.value)+1 if setting else 1



class SecuenceGenerator:
    @staticmethod
    def get_next_number(prefix)->int:
        
        if prefix == None:
            raise ValueError('Prefix at service SecuenceGenerator')

        counter = AppSetting.query.filter(AppSetting.key == prefix).first()

        #pendiente crer contunres

        if counter:
            n= int(counter.value) + 1
            counter.value = n
            return int(n)
        else:
            new_setting = AppSetting(key = prefix, 
                                     value = 1)
            db.session.add(new_setting)
            return 1