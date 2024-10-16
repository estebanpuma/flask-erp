from app import db

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
    def create_sale_order():
        from .models import SaleOrder
        pass

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