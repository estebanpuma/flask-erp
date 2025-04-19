from app import db

from flask import current_app

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
    def create_sale_order(
                            order_info:dict
                          ):
        
        try:
            print('esta es la order info')
         
            new_sale_order = SaleServices.create_sale_order(
                                                            order_number = order_info['general']['order_number'],
                                                            order_date = order_info['general']['request_date'],
                                                            delivery_date = order_info['general']['delivery_date'],
                                                            status = order_info.get('status', 'Pendiente'),
                                                            delivery_address = order_info.get('delivery_address', 'Quito'),
                                                            client_id = 1,
                                                            sales_person_id = order_info['general']['salesperson']
                                                            )
            

        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al gurdar orden de venta. e:{e}')
    
    @staticmethod
    def save_sale_order(
                            order_number:int,
                            order_date:str,
                            delivery_date: str,
                            status:str,
                            delivery_address: str,
                            client_id: int,
                            sales_person_id: int
                          ):
        from .models import SaleOrder
        print('entra a save sale order')
        try:

            new_sale_order = SaleOrder(order_number = order_number,
                                    order_date = order_date,
                                    delivery_date = delivery_date,
                                    status = 'Pendiente',
                                    delivery_addressc= delivery_address,
                                    client_id = client_id,
                                    sales_person_id = sales_person_id
                                    )
            db.session.add(new_sale_order)
            db.session.flush()
            print('in session')
            print(new_sale_order)
            return new_sale_order

        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error guardando orden de venta. e:{e}')
            raise Exception(str(e))
    

    @staticmethod
    def save_sale_order_product(  
                                    order_id:int,   
                                    product_id:int,
                                    #product_code:str,
                                    size:float,
                                    qty:int,
                                    price:float,
                                    notes:str
                                ):
        from .models import SaleOrderProduct
        try:
            new_sale_order_product = SaleOrderProduct(
                                                        order_id = order_id,
                                                        product_id = product_id,
                                                        size = size,
                                                        qty = qty,
                                                        price = price,
                                                        notes = notes
                                                    )
            
            db.session.add(new_sale_order_product)
            
            return new_sale_order_product
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al guardar los productos a la orden. e:{e}')
            raise Exception(str(e))
        
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