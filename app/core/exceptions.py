from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AppError(Exception):
    """Base para errores controlados de la app.

    Atributos:
      - message: mensaje principal para cliente/consumidor.
      - code: identificador estable del tipo de error.
      - status_code: código HTTP sugerido.
      - details: datos adicionales serializables.
    """

    message: str = "Ocurrió un error en la aplicación"
    code: str = "app_error"
    status_code: int = 500
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "error": self.message,
            "code": self.code,
            "message": self.message,
            "status": self.status_code,
        }
        if self.details:
            payload["details"] = self.details
        return payload


class ValidationError(AppError):
    def __init__(self, message: str = "Datos inválidos", **kwargs: Any):
        super().__init__(
            message=message,
            code="validation_error",
            status_code=400,
            **kwargs,
        )


class ConflictError(AppError):
    def __init__(self, message: str = "Conflicto de datos", **kwargs: Any):
        super().__init__(
            message=message,
            code="conflict_error",
            status_code=409,
            **kwargs,
        )


class NotFoundError(AppError):
    def __init__(self, message: str = "Recurso no encontrado", **kwargs: Any):
        super().__init__(
            message=message,
            code="not_found",
            status_code=404,
            **kwargs,
        )
