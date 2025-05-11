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
        sale = SaleOrder.query.get_or_404(sale_id)
        return sale
    
    @staticmethod
    def create_order(data):
        order = SaleOrder(
            order_number=data['order_number'],
            order_date=datetime.strptime(data['order_date'], "%Y-%m-%d").date(),
            delivery_date=datetime.strptime(data['delivery_date'], "%Y-%m-%d").date() if data.get('delivery_date') else None,
            status=data['status'],
            delivery_address=data.get('delivery_address'),
            client_id=data['client_id'],
            sales_person_id=data['sales_person_id']
        )

        for item in data['order_products']:
            order_item = SaleOrderProduct(
                product_id=item['product_id'],
                size=item.get('size'),
                qty=item['qty'],
                price=Decimal(item['price']),
                discount=Decimal(item.get('discount', 0)),
                notes=item.get('notes')
            )
            order.order_products.append(order_item)

        db.session.add(order)
        db.session.commit()
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