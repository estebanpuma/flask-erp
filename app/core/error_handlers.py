from flask import jsonify

from .exceptions import AppError, ConflictError, NotFoundError, ValidationError


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(ConflictError)
    def handle_conflict_error(error):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(500)
    def base_error_handler(error):
        app.logger.exception("Unhandled internal server error", exc_info=error)
        return jsonify({"error": "Error interno del servidor", "code": "internal_error"}), 500

    @app.errorhandler(404)
    def error_404_handler(error):
        return jsonify({"error": str(error), "code": "http_not_found"}), 404
