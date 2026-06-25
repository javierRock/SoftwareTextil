"""Manejadores de errores HTTP para Flask."""

from flask import Flask, jsonify

from software_textil.application.errors import AppError, ValidationError


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({"error": error.code, "message": error.message}), error.status_code

    @app.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        validation_error = ValidationError(str(error))
        return jsonify({"error": validation_error.code, "message": validation_error.message}), 400

    @app.errorhandler(KeyError)
    def handle_key_error(error: KeyError):
        campo = str(error).strip("'")
        return jsonify({"error": "validation_error", "message": f"Campo requerido: {campo}"}), 400
