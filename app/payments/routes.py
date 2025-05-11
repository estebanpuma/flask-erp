from flask import render_template, redirect, request, flash, url_for

from .services import PaymentServices
from .forms import PaymentMethodForm

from . import payments_bp


@payments_bp.route('/index')
def index():
    title = 'Pagos'
    prev_url = url_for('sales.index')

    return render_template('payments/index.html',
                           title = title,
                           prev_url = prev_url)


@payments_bp.route('/payment_methods')
def view_payment_methods():
    title = 'Metodos de pago'
    prev_url = url_for('payments.index')
    return render_template('payments/view_payment_methods.html',
                           title = title,
                           prev_url = prev_url)


@payments_bp.route('/payment_methods/<int:payment_method_id>')
def view_payment_method(payment_method_id):
    title = 'Metodo de pago'
    prev_url = url_for('payments.view_payment_methods')
    return render_template('payments/view_payment_method.html',
                           title = title,
                           prev_url = prev_url,
                           payment_method_id = payment_method_id)


@payments_bp.route('/create_payment_method', methods=['GET', 'POST'])
def add_payment_method():
    title = 'Nuevo metodo de pago'
    prev_url = url_for('payments.index')
    form = PaymentMethodForm()
    if form.validate_on_submit():
        
        try:
            PaymentServices.create_payment_method(form.name.data, form.description.data)
            flash('Metodo creado correctamente', 'success')
            return redirect(url_for('payments.view_payment_methods'))
        except Exception:
            flash('Error al crear el metodo de pago', 'danger')

    return render_template('payments/add_payment_method.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)