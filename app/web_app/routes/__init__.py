
from .materials import materials_bp
from .dashboards import dashboards_bp
from .products import products_bp
from .clients import clients_bp
from .suppliers import suppliers_bp
from .workers import workers_bp
from .payments import payments_bp
from .users import users_bp


def register_frontend_routes(app):
    app.register_blueprint(materials_bp)
    app.register_blueprint(dashboards_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(workers_bp)