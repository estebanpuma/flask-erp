import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s [in %(pathname)s:%(lineno)d]"


def configure_logging(app) -> None:
    """Configura logging global para Flask app y logger raíz del proyecto."""
    log_dir = app.config.get("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    app_log_level = app.config.get("LOG_LEVEL", "INFO")
    level = getattr(logging, str(app_log_level).upper(), logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT)

    info_handler = RotatingFileHandler(
        os.path.join(log_dir, "info.log"),
        maxBytes=app.config.get("LOG_MAX_BYTES", 10240),
        backupCount=app.config.get("LOG_BACKUP_COUNT", 10),
    )
    info_handler.setLevel(level)
    info_handler.setFormatter(formatter)

    warning_handler = RotatingFileHandler(
        os.path.join(log_dir, "warning.log"),
        maxBytes=app.config.get("LOG_MAX_BYTES", 10240),
        backupCount=app.config.get("LOG_BACKUP_COUNT", 10),
    )
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    app.logger.handlers.clear()
    app.logger.addHandler(info_handler)
    app.logger.addHandler(warning_handler)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(level)
    app.logger.propagate = False
