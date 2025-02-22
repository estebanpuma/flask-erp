from flask import render_template, redirect, url_for, flash, request

from .forms import StockOrderForm, ProductionOrderForm

from .services import ProductionServices, StockOrderServices, ProductionRequestServices

from . import production_bp

@production_bp.route('/production/index')
def index():
    title = 'Producción'
    prev_url = url_for('public.index')
    return render_template('production/index.html',
                           title = title,
                           prev_url = prev_url)


@production_bp.route('/stock_order')
def view_stock_orders():
    title = 'Pedidos para stock'
    prev_url = url_for('production.index')

    stock_orders = StockOrderServices.get_all_stock_orders()

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
                           prev_url = prev_url,
                           stock_order_id=stock_order_id)


@production_bp.route('/stock_order/create', methods=['GET','POST'])
def add_stock_order():
    title = 'Nuevo Pedido para Stock'
    prev_url = url_for('production.view_stock_orders')
    form = StockOrderForm()

    if form.validate_on_submit():
        try:
            new_order = StockOrderServices.create_stock_order(stock_order_code=form.code.data,
                                                            request_date = form.request_date.data,
                                                            delivery_date = form.delivery_date.data,
                                                            responsible_id = form.responsible.data,
                                                            notes = form.notes.data,
                                                            items = form.items.data)
        
            flash('Orden de Stock guardada con exito', 'success')
            return redirect(url_for('production.view_stock_orders'))
        except Exception as e:
            flash('Oucrrio un error', 'danger')

    form_data = {
        'fields': form.data,
        'errors': form.errors
    }

    return render_template('production/add_stock_order.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           form_data = form_data
                           )


@production_bp.route('/stock_orders/<int:stock_order_id>/delete', methods=['GET', 'POST'])
def delete_stock_order(stock_order_id):
    try:
        StockOrderServices.delete_stock_order(stock_order_id)
        flash('Registro eliminado', 'success')
        return redirect(url_for('production.view_stock_orders'))
    except Exception as e:
        raise Exception(f'Error al borrar registro. e:{e}')
        
    


#*********************Requerimientos de produccion************************************

@production_bp.route('/production_requests')
def view_production_requests():
    title = 'Requerimientos de produccion'
    prev_url = url_for('production.index')
    production_requests = ProductionRequestServices.get_all_production_requests()
    print(production_requests)
    return render_template('production/view_production_requests.html',
                           title = title,
                           prev_url = prev_url,
                           production_requests = production_requests)


@production_bp.route('/production_requests/<int:production_request_id>')
def view_production_request(production_request_id):
    title = 'Requerimiento'
    prev_url = url_for('production.view_production_requests')
    production_request = ProductionRequestServices.get_production_request(production_request_id)
    return render_template('production/view_production_request.html',
                           title = title,
                           prev_url = prev_url,
                           production_request_id = production_request_id,
                           production_request = production_request)


#***********************Ordenes de produccion***************************************************

@production_bp.route('/production_orders')
def view_production_orders():
    title = 'Ordenes de Produccion'
    prev_url = url_for('production.index')
    return render_template('production/view_production_orders.html',
                           title = title,
                           prev_url = prev_url)


@production_bp.route('/production_orders/<int:production_order_id>')
def view_production_order(production_order_id):
    title = 'Orden de Produccion'
    prev_url = url_for('production.view_production_orders')

    
    return render_template('production/view_production_order.html',
                           title = title,
                           prev_url = prev_url,
                           production_order_id = production_order_id)


@production_bp.route('/production_orders/create', methods=['GET', 'POST'])
def add_production_order():
    title = 'Nueva Orden de Produccion'
    prev_url = url_for('production.view_production_orders')
    form = ProductionOrderForm()

    if form.validate_on_submit():
        flash(form.data)
        try:
            new_po = ProductionServices.create_production_order(code=form.order_number.data,
                                                                scheduled_start_date = form.scheduled_start_date.data,
                                                                scheduled_end_date = form.scheduled_start_date.data,
                                                                responsible_id = form.responsible.data,
                                                                notes = form.notes.data,
                                                                items = form.items.data)
            flash('Registro uardado con exito')
            return redirect(url_for('production.view_production_orders'))
        except Exception as e:
            flash(f'Ocurrio un error. e{e}', 'danger')
    else:
        flash(form.errors)
    
    return render_template('production/add_production_order.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)


@production_bp.route('/delete_production_order/<int:order_id>')
def delete_production_order(order_id):
    try:
        ProductionServices.delete_production_order(order_id)
        flash('Orden eliminada', 'success')
        return redirect(url_for('production.view_production_orders'))
    except Exception as e:
        flash(f'Ocurrio un error e:{e}', 'danger')
        return str(e)