import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

migrate = Migrate()


def create_app(config):

    app = Flask(
        __name__,
        static_folder="web_app/static",  # aquí van tus imágenes / media
        static_url_path="/static",
        template_folder="web_app/templates",
    )

    app.config.from_object(config)
    CORS(app, resources={r"/media/*": {"origins": "*"}})
    jwt = JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)

    for folder in app.config["UPLOAD_FOLDERS"].values():
        os.makedirs(folder, exist_ok=True)

    from .storage.local import LocalStorageService

    storage_svc = LocalStorageService()
    app.extensions["storage_service"] = storage_svc

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

    from .logs import setup_logging

    setup_logging(app)

    # API V1 blueprints

    from .admin.api import admin_api_bp

    app.register_blueprint(admin_api_bp)

    from .crm.api import crm_api_bp

    app.register_blueprint(crm_api_bp)

    from .core.api import core_api_bp

    app.register_blueprint(core_api_bp)

    from .materials.api import materials_api_bp

    app.register_blueprint(materials_api_bp)

    from .sales.api import sales_api_bp

    app.register_blueprint(sales_api_bp)

    from .suppliers.api import suppliers_api_bp

    app.register_blueprint(suppliers_api_bp)

    from .products.api import products_api_bp

    app.register_blueprint(products_api_bp)

    from .auth.api import auth_bp

    app.register_blueprint(auth_bp)

    from .payments.api import payments_api_v1_bp

    app.register_blueprint(payments_api_v1_bp)

    from .production.api import production_api_bp

    app.register_blueprint(production_api_bp)

    from .inventory.api import inventory_api_bp

    app.register_blueprint(inventory_api_bp)

    from .media.api import media_api_bp

    app.register_blueprint(media_api_bp)

    # routes blueprints
    from .common import common_bp

    app.register_blueprint(common_bp)

    # frontend blueprints
    from .web_app import init_web_app, web_app_bp

    init_web_app(web_app_bp)
    app.register_blueprint(web_app_bp)

    return app
