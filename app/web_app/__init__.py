from .routes import register_frontend_routes
from flask import Blueprint
#def init_web_app(app):
#    register_frontend_routes(app)

web_app_bp = Blueprint(
    'web_app',
    __name__,
    template_folder='templates',      # tu carpeta web_app/templates
    static_folder='static',           # y aquí los CSS/JS de frontend     # para que no choquen con /static/media
    static_url_path='/static'
)

def init_web_app(bp):
    
    register_frontend_routes(bp)
