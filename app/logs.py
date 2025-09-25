import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """Configuracion de los loggers."""
    if not os.path.exists("logs"):
        os.mkdir("logs")

    info_handler = RotatingFileHandler("logs/info.log", maxBytes=10240, backupCount=10)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )

    warning_handler = RotatingFileHandler(
        "logs/warning.log", maxBytes=10240, backupCount=10
    )
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )

    app.logger.addHandler(info_handler)
    app.logger.addHandler(warning_handler)
    app.logger.setLevel(logging.INFO)  # Configura el nivel de logging general
