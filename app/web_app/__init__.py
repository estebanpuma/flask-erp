from .routes import register_frontend_routes

def init_web_app(app):
    register_frontend_routes(app)