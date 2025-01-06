from flask import render_template, redirect, url_for, request, flash, session

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
    
    session["sale_order"] = {
        "general": {},   # Datos Generales
        "client": {},   # Datos del Cliente
        "products": [], # Lista de productos
        "payment": {}       # Datos del pago
    }
    
    return redirect(url_for('sales.add_sale_order_products_info'))


@sales_bp.route('/sale-order/info', methods=['GET', 'POST'])
def add_sale_order_info():
    title = 'Orden de venta'
    
    next_url = url_for('sales.add_sale_order_client_info')
    from .forms import GeneralOrderInfoForm
    form = GeneralOrderInfoForm()
    prev_url = None
    if form.validate_on_submit():
        
        session["sale_order"]["general"] = {
            "order_number": request.form.get("order_number"),
            "request_date": request.form.get("request_date"),
            "delivery_date": request.form.get("delivery_date"),
            "salesperson": request.form.get("salesperson")
        }
        session.modified = True
        flash(session)
        #return redirect(url_for("sales.sale_order_checkout"))
    
    

    return render_template('sales/new-order/add_sale_order_info.html',
                           title = title,
                           prev_url = prev_url,
                           next_url = next_url,
                           form = form
                           )


@sales_bp.route('/sale-order/client-info', methods=['GET', 'POST'])
def add_sale_order_client_info():
    title = 'Orden de Venta/Cliente'
    prev_url = url_for('sales.add_sale_order_products_info')
    next_url = url_for('sales.add_sale_order_payment_info')
    form = ClientForm()

    if form.validate_on_submit():

        session["sale_order"]["client"] = form.data
        session.modified = True
        
        return redirect(url_for('sales.add_sale_order_payment_info'))
    else:
        flash('error', 'danger')
        flash(form.errors)
    
    return render_template('sales/new-order/add_sale_order_client_info.html',
                           title = title,
                           prev_url = prev_url,
                           next_url = next_url,
                           form = form)


@sales_bp.route('/sale-order/products-info', methods=['GET', 'POST'])
def add_sale_order_products_info():
    title = 'Orden de Venta/Productos'
    prev_url = url_for('sales.view_sale_orders')
    next_url = url_for('sales.add_sale_order_client_info')
    
    from .forms import ProductOrderForm

    form = ProductOrderForm()


    if form.validate_on_submit():
        session["sale_order"]["products"] =''
        for order in form.order.data: 
            new_product = order
            session["sale_order"]["products"].append(new_product)
            session.modified = True
        return redirect(url_for('sales.add_sale_order_client_info'))
    else:
        flash(form.errors)

    return render_template('sales/new-order/add_sale_order_products_info.html',
                           title = title,
                           prev_url = prev_url,
                           next_url = next_url,
                           form = form)


@sales_bp.route('/sale-order/payment-info', methods=['GET', 'POST'])
def add_sale_order_payment_info():
    title = 'Orden de Venta/Pago'
    prev_url = url_for('sales.add_sale_order_products_info')
    next_url = url_for('sales.sale_order_checkout')
    from .forms import PaymentForm
    form = PaymentForm()
    if form.validate_on_submit():
        session['sale_order']['payment']=form.data
        
        flash(session)
    else:
        flash(form.errors)

    return render_template('sales/new-order/add_sale_order_payment_info.html',
                           title = title,
                           form = form,
                           prev_url = prev_url,
                           next_url = next_url
                           )


@sales_bp.route('/sale-order/checkout', methods=['GET', 'POST'])
def sale_order_checkout():
    title = 'Orden de Venta/Checkout'
    prev_url = url_for('sales.add_sale_order_payment_info')
    


    return render_template('sales/new-order/sale_order_checkout.html',
                           title = title,
                           prev_url = prev_url)


