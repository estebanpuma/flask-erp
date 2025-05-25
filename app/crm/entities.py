import re

from ..core.exceptions import ValidationError

from ..common.parsers import parse_phone, parse_ruc_or_ci, parse_bool, parse_int, parse_str

from datetime import datetime

class ClientEntity:
    def __init__(self, data: dict, is_update=False):
        self.name = parse_str(data.get("name"))
        self.ruc_or_ci = parse_ruc_or_ci(data.get("ruc_or_ci"))
        self.phone = parse_phone(data.get("phone"))
        self.email = parse_str(data.get("email"))
        self.address = parse_str(data.get("address"))
        self.client_type = parse_str(data.get("client_type"))
        self.province_id = parse_int(data.get("province_id"))
        self.canton_id = parse_int(data.get("canton_id"))
        self.client_category_id = parse_int(data.get("client_category_id"))
        self.is_special_taxpayer = parse_bool(data.get("is_special_taxpayer"))
        self.is_special_taxpayer = bool(data.get('is_special_taxpayer', False))

        self._validate(is_update)


    def _validate(self, is_update=False):
        if not self.name:
            raise ValidationError("El nombre es obligatorio.")
        if not self.ruc_or_ci or not re.match(r'^\d{10}$|^\d{13}$', self.ruc_or_ci):
            raise ValidationError("El RUC debe tener 13 dígitos o la cédula 10 dígitos.")
        if not self.phone:
            raise ValidationError("El teléfono es obligatorio.")
        if not self.client_type:
            raise ValidationError("El tipo de cliente es obligatorio.")
        if not self.address:
            raise ValidationError("La dirección es obligatoria.")
        if not self.province_id:
            raise ValidationError("La provincia es obligatoria.")
        if not self.canton_id:
            raise ValidationError("El cantón es obligatorio.")
        if self.email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.email):
            raise ValidationError("Correo electrónico inválido.")
        
        
class ClientCategoryEntity:
    def __init__(self, data: dict):
        self.name = data.get('name', '').strip()
        self.description = data.get('description')

        self._validate()

    def _validate(self):
        if not self.name:
            raise ValidationError("El nombre de la categoría es obligatorio.")
        


class ContactEntity:
    def __init__(self, data: dict):
        self.name = parse_str(data.get("name"))
        self.email = parse_str(data.get("email"))
        self.phone = parse_str(data.get("phone"))
        self.position = parse_str(data.get("position"))
        self.notes = parse_str(data.get("notes"))
        self.client_id = parse_int(data.get("client_id"))
        
        birth = data.get("birth_date")
        self.birth_date = None
        if birth:
            try:
                self.birth_date = datetime.strptime(str(birth), "%Y-%m-%d").date()
            except:
                raise ValidationError("Formato de fecha inválido. Usa YYYY-MM-DD.")

        self._validate()

    def _validate(self):
        if not self.name:
            raise ValidationError("El nombre del contacto es obligatorio.")
        if not self.client_id:
            raise ValidationError("Debe asignarse a un cliente.")