from app import db

from .models import AppSetting


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
        key = ProductCodeGenerator.get_model_counter_key(
            linea, sublinea, tipo, coleccion
        )
        app_settings_key = f"product_counter_{key}"
        setting = AppSetting.query.filter_by(key=app_settings_key).first()
        if not setting:
            setting = AppSetting(key=app_settings_key, value="1")
            db.session.add(setting)
            db.session.flush()
            return f"{key}001"
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
        key = ProductCodeGenerator.get_model_counter_key(
            linea, sublinea, tipo, coleccion
        )
        app_settings_key = f"product_counter_{key}"
        setting = AppSetting.query.filter_by(key=app_settings_key).first()
        if not setting:
            return f"{key}001"
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
        if tipo:
            key += tipo.code
        return f"collection_counter_{key}"

    @staticmethod
    def get_next_collection_number(linea, sublinea, tipo):
        key = CollectionCodeGenerator.get_counter_key(linea, sublinea, tipo)
        setting = AppSetting.query.filter_by(key=key).first()

        if not setting:
            setting = AppSetting(key=key, value="1")
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
        return int(setting.value) + 1 if setting else 1


class SecuenceGenerator:
    @staticmethod
    def set_obj(data: dict) -> str:
        """Devuelve el codigo autoincremental de un objeto según el tipo de objeto y el prefijo"""
        from ..materials.models import Material
        from ..products.models import Product, ProductCollection
        from .dto import ObjectCodePreviewDTO

        dto = ObjectCodePreviewDTO(**data)

        print(dto.object_type)

        objects = ["material", "product", "collection"]
        if dto.object_type not in objects:
            raise ValueError("Tipo de objeto no encontrado")
        obj_dict = {
            "material": Material,
            "product": Product,
            "collection": ProductCollection,
        }
        prefix = dto.prefix.upper()
        new_prefix = f"{dto.object_type.upper()}_{prefix}"

        # Obtener el objeto contador y el número inicial
        counter_obj, sec = SecuenceGenerator.get_sequence_object(new_prefix)

        obj = obj_dict[dto.object_type]
        print(obj)

        while True:
            next_code = f"{prefix}{sec:03d}"
            if not db.session.query(obj).filter_by(code=next_code).first():
                break  # Código disponible, salimos del bucle
            sec += 1  # Si el código existe, intentamos con el siguiente número

        # Actualizamos el valor final en el objeto contador que ya está en la sesión
        counter_obj.value = str(sec)

        return next_code

    @staticmethod
    def get_sequence_object(prefix: str) -> tuple[AppSetting, int]:
        """
        Obtiene el objeto AppSetting para un prefijo y su siguiente número.
        Añade el objeto a la sesión si no existe.
        Devuelve el objeto y el siguiente número.
        """
        if prefix is None:
            raise ValueError("Prefix at service SecuenceGenerator")

        counter = db.session.query(AppSetting).filter_by(key=prefix).first()

        if not counter:
            counter = AppSetting(
                key=prefix, value="0"
            )  # Empezamos en 0 para que el primer número sea 1
            db.session.add(counter)

        next_number = int(counter.value) + 1
        return counter, next_number
