
from flask import Flask, render_template, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

from flask_login import LoginManager

from jinja2 import TemplateNotFound

from flask_restful import Api

from flask_wtf.csrf import CSRFProtect


csrf = CSRFProtect()

api = Api(decorators=[csrf.exempt])
db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

def create_app(config):
    print(config)
    app = Flask(__name__)
    app.config.from_object(config)
    
    login_manager.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from .logs import setup_logging
    setup_logging(app)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .common import common_bp
    app.register_blueprint(common_bp)

    from .crm import crm_bp
    app.register_blueprint(crm_bp)

    from .inventory import inventory_bp
    app.register_blueprint(inventory_bp)

    from .production import production_bp
    app.register_blueprint(production_bp)

    from .products import products_bp
    app.register_blueprint(products_bp)

    from .payments import payments_bp
    app.register_blueprint(payments_bp)

    from .public import public_bp
    app.register_blueprint(public_bp)

    from .sales import sales_bp
    app.register_blueprint(sales_bp)

    with app.app_context():
        from .admin.services import AdminServices 
        #AdminServices.initialize_admin_user()

    return app


def register_error_handlers(app):

    @app.errorhandler(500)
    def base_error_handler():
        return render_template('500.html'), 500
    
    @app.errorhandler(404)
    def error_404_handler():
        return render_template('404.html'), 404
    
    @app.errorhandler(api)
    def handle_abort(err):
        response = jsonify({'message': err['message']})
        response.status_code = err['status']
        return response
    
    @app.errorhandler(TemplateNotFound)
    def handle_template_not_found():
         return render_template('error.html', message="Lo sentimos, la página que buscas no se pudo encontrar."), 404
    