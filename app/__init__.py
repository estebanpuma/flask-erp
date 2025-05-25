
from flask import Flask, jsonify

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

from flask_jwt_extended import JWTManager



db = SQLAlchemy()

migrate = Migrate()



def create_app(config):
    print(config)
    app = Flask(__name__)
    app.config.from_object(config)
    
    jwt = JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from .core.error_handlers import register_error_handlers
    register_error_handlers(app)

    @jwt.unauthorized_loader
    def missing_token_callback(err):
        return {"msg": "Token de acceso requerido"}, 401

    @jwt.expired_token_loader
    def expired_token_callback(expired_token):
        return {"msg": "Token expirado"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(err):
        return {"msg": f"Token inválido, {err}"}, 422
    
    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Token inválido", "reason": reason}), 401

    from .logs import setup_logging
    setup_logging(app)

    #API V1 blueprints
    
    from .crm.api import crm_api_bp
    app.register_blueprint(crm_api_bp)

    from .core.api import core_api_bp
    app.register_blueprint(core_api_bp)

    from .materials.api import materials_api_bp
    app.register_blueprint(materials_api_bp)

    from .sales.api import sales_api_bp
    app.register_blueprint(sales_api_bp)

    from .products.api import products_api_bp
    app.register_blueprint(products_api_bp)

    from .auth.api import auth_bp
    app.register_blueprint(auth_bp)

    from .payments.api import payments_api_v1_bp
    app.register_blueprint(payments_api_v1_bp)

    from .production.api import production_api_bp
    app.register_blueprint(production_api_bp)
    
    

    #routes blueprints
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .common import common_bp
    app.register_blueprint(common_bp)

    from .crm import crm_bp
    app.register_blueprint(crm_bp)

    from .finance import finance_bp
    app.register_blueprint(finance_bp)

    from .inventory import inventory_bp
    app.register_blueprint(inventory_bp)

    from .pricing import pricing_bp
    app.register_blueprint(pricing_bp)

    from .materials import materials_bp
    app.register_blueprint(materials_bp)

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


    