from flask import Blueprint

from .routes import register_frontend_routes
from .ui_labels import inject_ui_labels

web_app_bp = Blueprint(
    "web_app",
    __name__,
    template_folder="templates",  # tu carpeta web_app/templates
    static_folder="static",  # y aquí los CSS/JS de frontend     # para que no choquen con /static/media
    static_url_path="/static",
)

web_app_bp.context_processor(inject_ui_labels)


def init_web_app(bp):

    register_frontend_routes(bp)
