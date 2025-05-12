from app import db

from flask import current_app

from .models import SaleOrder, SaleOrderProduct

from datetime import datetime
from decimal import Decimal

class SaleServices:

    @staticmethod
    def get_all_sales():
        from .models import SaleOrder
        sales = SaleOrder.query.all()
        return sales
    
    @staticmethod
    def get_sale(sale_id):
        from .models import SaleOrder
        sale = SaleOrder.query.get(sale_id)
        return sale
    
    @staticmethod
    def create_sale_order(order_number, order_date, status, client_id, sales_person_id,
                          delivery_date=None, delivery_address=None, order_products=[]):

        order = SaleOrder(
            order_number=order_number,
            order_date=order_date,
            delivery_date=delivery_date,
            delivery_address=delivery_address,
            status=status,
            client_id=client_id,
            sales_person_id=sales_person_id
        )

        for item in order_products:
            order_item = SaleOrderProduct(
                product_id=item['product_id'],
                qty=item['qty'],
                size=item.get('size'),
                price=Decimal(item['price']),
                discount=Decimal(item.get('discount', 0)),
                notes=item.get('notes')
            )
            order.order_products.append(order_item)

        db.session.add(order)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return order

        
    @staticmethod
    def save_payment_plan(
        sale_order_id:int,
        total_amount:float,
        payment_method_id:int,
        total_installments:int
        ):
        from ..payments.models import PaymentPlan
        try:
            new_payment_plan = PaymentPlan(
                                            sale_order_id = sale_order_id,
                                            total_amount = total_amount,
                                            payment_method_id = payment_method_id,
                                            total_installments = total_installments
            )
            db.session.add(new_payment_plan)
            return new_payment_plan
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al guardar el plan de pagos. e: {str(e)}')
            raise Exception(str(e))
        

    @staticmethod
    def save_installment(
        payment_plan_id: int,
        due_date: str,
        amount: float,
        paid_amount: float,
        status:str
    ):
    
        try:

            from ..payments.models import Installment
            new_installment = Installment(
                                            payment_plan_id = payment_plan_id,
                                            due_date = due_date,
                                            amount = amount,
                                            paid_amount = paid_amount,
                                            status = status
                                        )
            db.session.add(new_installment)
            return new_installment
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al guardar la cuota. e:{str(e)}')
            raise Exception(str(e))
        

    @staticmethod
    def get_new_sale_order_number():
        from .models import SaleOrder
        last_order = SaleOrder.query.order_by(SaleOrder.id.desc()).first()

        # Si no hay órdenes, comenzamos desde 1
        new_order_number = 1 if last_order is None else last_order.order_number + 1

        # Verificamos si el nuevo número de orden ya existe
        while SaleOrder.query.filter_by(order_number=str(new_order_number)).first() is not None:
            new_order_number += 1

        return new_order_number