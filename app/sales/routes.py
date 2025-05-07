from flask import render_template, redirect, url_for, request, flash, session

from flask_login import current_user

from ..crm.services import CRMServices

from .forms import ClientForm, CheckoutForm
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
    
    return render_template('sales/new-order/add_sale_order.html')


@sales_bp.route('/sale-order/info', methods=['GET', 'POST'])
def add_sale_order_info():
    title = 'Orden de venta'
    
    next_url = url_for('sales.sale_order_checkout')
    order_number = SaleServices.get_new_sale_order_number()
    print('order_number', order_number)
    session["sale_order"]["order_number"] = order_number
    from .forms import GeneralOrderInfoForm
    form = GeneralOrderInfoForm()
    prev_url = url_for('sales.add_sale_order_payment_info')
    if form.validate_on_submit():
        
        session["sale_order"]["general"] = {
            "order_number": request.form.get("order_number"),
            "request_date": request.form.get("request_date"),
            "delivery_date": request.form.get("delivery_date"),
            "salesperson": request.form.get("salesperson")
        }
        session["sale_order"]["order_number"] = form.data.get("order_number")
        session.modified = True
        
        return redirect(url_for("sales.sale_order_checkout"))
    
    

    return render_template('sales/new-order/add_sale_order_info.html',
                           title = title,
                           prev_url = prev_url,
                           next_url = next_url,
                           form = form,
                           order_number=order_number
                           )


@sales_bp.route('/sale-order/client-info', methods=['GET', 'POST'])
def add_sale_order_client_info():
    title = 'Orden de Venta/Cliente'
    prev_url = url_for('sales.view_sale_orders')
    next_url = url_for('sales.add_sale_order_products_info')
    form = ClientForm()
    client = {}
    if 'client' in session['sale_order']:
        client = session['sale_order']['client']
        
    if form.validate_on_submit():

        client = CRMServices.get_client_by_ci(form.ruc_or_ci.data)
        if client is None:
            new_client = CRMServices.create_client(ruc_or_ci = form.ruc_or_ci.data,
                                               client_type = form.client_type.data,
                                               name = form.name.data,
                                               city = form.city.data,
                                               address = form.address.data,
                                               phone = form.phone.data,
                                               email = form.email.data)
            flash('Cliente guardado', 'success')

        session["sale_order"]["client"] = form.data
        session.modified = True
        
        return redirect(url_for('sales.add_sale_order_products_info'))
    
    else:
        flash(form.errors)
    return render_template('sales/new-order/add_sale_order_client_info.html',
                           title = title,
                           prev_url = prev_url,
                           next_url = next_url,
                           form = form,
                           client = client
                           )


@sales_bp.route('/sale-order/products-info', methods=['GET', 'POST'])
def add_sale_order_products_info():
    title = 'Orden de Venta/Productos'
    prev_url = url_for('sales.add_sale_order_client_info')
    next_url = url_for('sales.add_sale_order_payment_info')
    
    from .forms import ProductOrderForm

    form = ProductOrderForm()
    products = []
    if 'products' in session['sale_order']:
        products = session['sale_order']['products']
        print('products', products)

    if form.validate_on_submit():
        session["sale_order"]["products"] =[]
        for order in form.order.data: 
            new_product = order
            session["sale_order"]["products"].append(new_product)
        total_items = form.total_items.data
        total_amount = form.total_amount.data
        session["sale_order"]["total_items"] = total_items
        session["sale_order"]["total_amount"] = total_amount
        session.modified = True
        return redirect(url_for('sales.add_sale_order_payment_info'))

    return render_template('sales/new-order/add_sale_order_products_info.html',
                           title = title,
                           prev_url = prev_url,
                           next_url = next_url,
                           form = form,
                           products = products)


@sales_bp.route('/sale-order/payment-info', methods=['GET', 'POST'])
def add_sale_order_payment_info():
    title = 'Orden de Venta/Pago'
    prev_url = url_for('sales.add_sale_order_products_info')
    next_url = url_for('sales.add_sale_order_info')
    from .forms import PaymentForm
    
    form = PaymentForm()
    data = {}
    if 'payment' in session['sale_order']:
        data=session['sale_order']['payment']    
    
    total_amount = session["sale_order"].get("total_amount", 0)
    
    if form.validate_on_submit():
        session['sale_order']['payment'] = form.data
        
        session.modified = True
        return redirect(url_for('sales.add_sale_order_info'))


    return render_template('sales/new-order/add_sale_order_payment_info.html',
                           title=title,
                           form=form,
                           prev_url=prev_url,
                           next_url=next_url,
                           total_amount=total_amount,
                           data=data,
                           )


@sales_bp.route('/sale-order/checkout', methods=['GET', 'POST'])
def sale_order_checkout():
    title = 'Orden de Venta/Checkout'
    prev_url = url_for('sales.add_sale_order_payment_info')
    form = CheckoutForm()

    order_resume = session["sale_order"]  

    if request.method == 'POST':
        print('se posteo el checkout')
        SaleServices.create_sale_order(order_resume)

        flash('Orden de venta creada con exito', 'success')
    return render_template('sales/new-order/sale_order_checkout.html',
                           title = title,
                           prev_url = prev_url,
                           order_resume = order_resume,
                           form = form
                           )


