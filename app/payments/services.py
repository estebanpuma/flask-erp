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
    
    
    ###metodo de plan de pago PaymentMethod
    @staticmethod
    def get_payment_plan(id):
        payment_plan = PaymentPlan.query.get(id)
        if not payment_plan:
            raise NotFoundError('Plan de pago no encontrado')
        return payment_plan
    
    @staticmethod
    def get_payment_plans():
        payment_plans = PaymentPlan.query.all()
        return payment_plans

    @staticmethod
    def create_payment_plan(sale_order_id, payment_method_id, total_amount, total_installments=None):
        # Validar que la orden y método existen
        from ..sales.models import SaleOrder
        order = SaleOrder.query.get(sale_order_id)
        if not order:
            raise NotFoundError("Orden de venta no encontrada.")

        method = PaymentMethod.query.get(payment_method_id)
        if not method:
            raise NotFoundError("Método de pago no encontrado.")

        plan = PaymentPlan(
            sale_order_id=sale_order_id,
            payment_method_id=payment_method_id,
            total_amount=total_amount,
            total_installments=total_installments
        )

        db.session.add(plan)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return plan