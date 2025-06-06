
#from .products_routes import products_bp
#from .sales_routes import sales_bp
from .materials import materials_bp
from .dashboards import dashboards_bp

def register_frontend_routes(app):
    app.register_blueprint(materials_bp)
    app.register_blueprint(dashboards_bp)
