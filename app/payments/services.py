from .models import PaymentMethod, PaymentPlan, Installment
from flask import current_app
from app import db

from ..core.exceptions import *


class PaymentServices:

    @staticmethod
    def get_all_payment_methods():
        methods = PaymentMethod.query.all()
        return methods
    

    @staticmethod
    def get_payment_method(id):
        method = PaymentMethod.query.get(id)
        return method


    @staticmethod
    def create_payment_method(name, description=None):
        existing = PaymentMethod.query.filter_by(name=name.strip()).first()
        if existing:
            raise ConflictError("Ya existe un método de pago con ese nombre.")

        method = PaymentMethod(name=name.strip(), description=description)

        db.session.add(method)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return method
    

    @staticmethod
    def update_payment_method(resource_id, data):
        method = PaymentMethod.query.get(resource_id)
        if not method:
            raise NotFoundError("Método de pago no encontrado.")

        if 'name' in data:
            name = data['name'].strip()
            existing = PaymentMethod.query.filter_by(name=name).first()
            if existing and existing.id != method.id:
                raise ConflictError("Ya existe un método de pago con ese nombre.")
            method.name = name

        if 'description' in data:
            method.description = data['description']

        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return method
    

    @staticmethod
    def delete_payment_method(resource_id):
        method = PaymentMethod.query.get(resource_id)
        if not method:
            raise NotFoundError("Método de pago no encontrado.")

        db.session.delete(method)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return True