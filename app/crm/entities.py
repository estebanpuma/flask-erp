import re

from ..core.exceptions import ValidationError


class ClientEntity:
    def __init__(self, data: dict, is_update=False):
        self.name = data.get('name')
        self.ruc_or_ci = data.get('ruc_or_ci')
        self.email = data.get('email')
        self.phone = data.get('phone')
        self.address = data.get('address')
        self.province_id = data.get('province_id')
        self.canton_id = data.get('canton_id')
        self.is_special_taxpayer = data.get('is_special_taxpayer')
        self.client_type = data.get('client_type')
        self.client_category_id = data.get('client_category')

        self._validate(is_update)
        

    def _validate(self, is_update=False):
        if not self.name:
            raise ValidationError("El nombre es obligatorio.")
        
        if not is_update:
            if not self.ruc_or_ci or not re.match(r'^\d{10}|\d{13}$', self.ruc_or_ci):
                raise ValidationError("RUC o cédula inválida.")
        
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