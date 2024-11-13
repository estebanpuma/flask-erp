from flask import render_template, redirect, url_for, flash

from .forms import StockOrderForm

from .services import ProductionSevices

from . import production_bp

@production_bp.route('/production/index')
def index():
    title = 'production'
    prev_url = url_for('public.index')
    return render_template('production/index.html',
                           title = title,
                           prev_url = prev_url)



@production_bp.route('/production_order')
def view_production_orders():
    title = 'Ordenes de Produccion'
    prev_url = url_for('production.index')


    return render_template('production/view_production_orders.html',
                           title = title,
                           prev_url = prev_url)


@production_bp.route('/production_order/<int:production_order_id>')
def view_production_order(production_order_id):
    title = 'Orden de Produccion'
    prev_url = url_for('production.view_production_orders')

    
    return render_template('production/view_production_order.html',
                           title = title,
                           prev_url = prev_url)


@production_bp.route('/production_order/create', methods=['GET', 'POST'])
def add_production_order():
    title = 'Nueva Orden de Produccion'
    prev_url = url_for('production.view_production_orders')

    
    return render_template('production/view_production_orders.html',
                           title = title,
                           prev_url = prev_url)


@production_bp.route('/stock_order')
def view_stock_orders():
    title = 'Pedidos para stock'
    prev_url = url_for('production.index')

    stock_orders = ProductionSevices.get_all_stock_orders()

    return render_template('production/view_stock_orders.html',
                           title = title,
                           prev_url = prev_url,
                           stock_orders = stock_orders)


@production_bp.route('/stock_order/<int:stock_order_id>')
def view_stock_order(stock_order_id):
    title = 'Pedido para stock'
    prev_url = url_for('production.view_stock_orders')

    return render_template('production/view_stock_order.html',
                           title = title,
                           prev_url = prev_url)


@production_bp.route('/stock_order/create')
def add_stock_order():
    title = 'Nuevo Pedido para Stock'
    prev_url = url_for('production.view_stock_orders')
    form = StockOrderForm()

    return render_template('production/add_stock_order.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)