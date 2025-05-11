class AppError(Exception):
    """Base para errores controlados de la app."""
    pass

class ValidationError(AppError):
    """Error por datos inválidos del usuario."""
    pass

class ConflictError(AppError):
    """Error por datos duplicados, conflictos lógicos."""
    pass

class NotFoundError(AppError):
    """Recurso no encontrado."""
    pass
