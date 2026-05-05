from .core.logger import configure_logging


def setup_logging(app):
    """Compatibilidad retroactiva: delega la configuración al logger central."""
    configure_logging(app)
