from flask import render_template, redirect, url_for, request, flash

from flask_login import current_user

from .forms import ClientForm
from .services import SaleServices
from . import sales_bp

@sales_bp.route('/sales/index')
def index():
    title = 'Modulo de Ventas'
    return render_template('sales/index.html',
                           title = title)


@sales_bp.route('/sale-orders')
def view_sale_orders():
    title = 'Ordenes de venta'
    prev_url = url_for('sales.index')
    
    sales = SaleServices.get_all_sales()

    return render_template('sales/view_sale_orders.html',
                           title = title,
                           prev_url = prev_url,
                           sales = sales)


@sales_bp.route('/sale-orders/<int:sale_id>')
def view_sale_order(sale_id):
    title = 'Orden de venta'
    prev_url = url_for('sales.index')
    
    sale = SaleServices.get_sale(sale_id)

    return render_template('sales/view_sale_order.html',
                           title = title,
                           prev_url = prev_url,
                           sale = sale)



#****************Proceso de orden de venta********************
#Este proceso tiene un entrypoint(add_sale_order) donde se inicializ la sesion
#El proceso fluye a traves de varias pantallas, cada pantalla almacena en sesion info relevante
#EL final del proceso es el checkout, una vez se confirma se guarda todo lo de la sesion en la base de datos
#Asi evito que si se cancela un orden no se queden registrados valores de alguna de las pantallas
#La info se guarda como una transaccion

@sales_bp.route('/sale-orders/create')
def add_sale_order():
    

    return redirect(url_for('sales.add_sale_order_info'))


@sales_bp.route('/sale-order/info')
def add_sale_order_info():
    title = 'Orden de venta'
    prev_url = url_for('sales.view_sale_orders')
    next_url = url_for('sales.add_sale_order_client_info')
    from app.common.utils import utc_now, get_today
    today = get_today()
    order_number = SaleServices.get_new_sale_order_number()
    salesperson = current_user
    from ..admin.services import AdminServices
    role_codes = ['VEN-GEN', 'VEN-SUP']
    salespersons = AdminServices.get_users_with_role(role_codes)

    return render_template('sales/new-order/add_sale_order_info.html',
                           title = title,
                           prev_url = prev_url,
                           next_url = next_url,
                           today = today,
                           order_number = order_number,
                           salespersons = salespersons)


@sales_bp.route('/sale-order/client-info', methods=['GET', 'POST'])
def add_sale_order_client_info():
    title = 'Orden de Venta/Cliente'
    prev_url = url_for('sales.add_sale_order_info')
    next_url = url_for('sales.add_sale_order_products_info')
    form = ClientForm()

    if form.validate_on_submit():
        flash(form.data, 'warning')
    
    return render_template('sales/new-order/add_sale_order_client_info.html',
                           title = title,
                           prev_url = prev_url,
                           next_url = next_url,
                           form = form)


@sales_bp.route('/sale-order/products-info')
def add_sale_order_products_info():
    title = 'Orden de Venta/Productos'
    prev_url = url_for('sales.add_sale_order_client_info')
    next_url = url_for('sales.add_sale_order_payment_info')

    return render_template('sales/new-order/add_sale_order_products_info.html',
                           title = title,
                           prev_url = prev_url,
                           next_url = next_url)


@sales_bp.route('/sale-order/payment-info')
def add_sale_order_payment_info():
    title = 'Orden de Venta/Pago'
    prev_url = url_for('sales.add_sale_order_products_info')
    next_url = url_for('sales.sale_order_checkout')

    return render_template('sales/new-order/add_sale_order_payment_info.html',
                           title = title,
                           prev_url = prev_url,
                           next_url = next_url
                           )


@sales_bp.route('/sale-order/checkout')
def sale_order_checkout():
    title = 'Orden de Venta/Checkout'
    prev_url = url_for('sales.add_sale_order_payment_info')


    return render_template('sales/new-order/sale_order_checkout.html',
                           title = title,
                           prev_url = prev_url)


