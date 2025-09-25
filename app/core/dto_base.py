from pydantic import BaseModel, ConfigDict
from pydantic import ValidationError as pValidation

from .exceptions import ValidationError


class MyBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    model_config = ConfigDict(protected_namespaces=("__",))

    @classmethod
    def validate_with_message(cls, data: dict | None = None, **kw):
        try:
            return cls.model_validate(data or kw)  # ✅ validación normal Pydantic v2
        except pValidation as e:
            # ⤵️   re-empacamos los errores con icono ⚠️
            raise ValidationError(
                [
                    {
                        "campo": err["loc"],  # ubicación → ('campo',)
                        "msg": f"⚠️ {err['msg']}",  # mensaje traducido
                        "tipo": err["type"],  # código original
                    }
                    for err in e.errors()
                ]
            ) from None
