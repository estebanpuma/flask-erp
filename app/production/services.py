from .models import StockOrder


class ProductionSevices:

    def get_all_stock_orders():
        stock_orders = StockOrder.query.all()
        return stock_orders

    def get_stock_order(stock_order_id):
        stock_order = StockOrder.query.get_or_404()
        return stock_order
    
    def get_next_so_code():
        last_stock_order = StockOrder.query.order_by(StockOrder.id.desc()).first()
        if last_stock_order:
            last_stock_order_number = int(last_stock_order.code) if last_stock_order.code else 0
            new_code = last_stock_order_number +1
        else:
            new_code = 1
        return str(new_code)

        