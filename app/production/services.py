
class ProductionSevices:

    def get_all_stock_orders():
        from .models import StockOrder
        stock_orders = StockOrder.query.all()
        return stock_orders
    

    def get_stock_order(stock_order_id):
        from .models import StockOrder
        stock_order = StockOrder.query.get_or_404()
        return stock_order