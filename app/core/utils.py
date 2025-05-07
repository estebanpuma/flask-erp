# app/core/utils.py

from flask import jsonify, make_response

def success_response(data=None, status_code=200):
    """
    Estandariza respuestas exitosas.
    """
    if data is None:
        data = {"message": "Operación exitosa"}
    return make_response(jsonify(data), status_code)


def error_response(message="Error inesperado", status_code=500):
    """
    Estandariza respuestas de error.
    """
    return make_response(jsonify({"message": message}), status_code)

def validation_error_response(errors):
    """
    Devuelve un error específico de validación.
    """
    return make_response(jsonify({"errors": errors}), 400)
