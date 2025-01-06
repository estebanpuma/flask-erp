from .models import PaymentMethod, PaymentPlan, Installment
from flask import current_app
from app import db


class PaymentMethodService:

    @staticmethod
    def get_all_payment_methods():
        methods = PaymentMethod.query.all()
        return methods
    
    @staticmethod
    def get_payment_method(id):
        method = PaymentMethod.query.get_or_404(id)
        return method

    def create_payment_method(name:str, description:str):
        try:
            new_payment_method = PaymentMethod(name = name,
                                               description = description)
            
            db.session.add(new_payment_method)
            db.session.commit()
            current_app.logger.info(f'Metodo de pago creado correctamente: {name}')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al crear metodo de pago, e:{e}')
            raise Exception(str(e))