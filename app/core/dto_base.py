from pydantic import  BaseModel, ConfigDict, ValidationError as pValidation
from .exceptions import ValidationError

class MyBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def validate_with_message(cls, data: dict | None = None, **kw):
        try:
            return cls.model_validate(data or kw)     # ✅ validación normal Pydantic v2
        except pValidation as e:
            # ⤵️   re-empacamos los errores con icono ⚠️
            raise ValidationError(
                [
                    {
                        'campo' : err['loc'],             # ubicación → ('campo',)
                        'msg' : f"⚠️ {err['msg']}",     # mensaje traducido
                        'tipo': err['type']             # código original
                    }
                    for err in e.errors()
                ]
            ) from None



