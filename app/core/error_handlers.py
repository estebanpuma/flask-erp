from flask import jsonify

from .exceptions import AppError, ConflictError, NotFoundError, ValidationError


def register_error_handlers(app):

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(ConflictError)
    def handle_conflict_error(e):
        return jsonify({"error": str(e)}), 409

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(e):
        return jsonify({"error": str(e)}), 404

    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({"error": str(e)}), 500

    @app.errorhandler(500)
    def base_error_handler(e):
        return jsonify({"error": str(e)}), 500

    @app.errorhandler(404)
    def error_404_handler(e):
        return jsonify({"error": str(e)}), 404
