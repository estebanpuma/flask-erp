from flask import Blueprint, render_template


payments_bp = Blueprint('payments', __name__, url_prefix='/payments', template_folder='../templates')


@payments_bp.route('/methods')
def payment_methods_list():
    return 'hola'

@payments_bp.route('/methods/<int:id>')
def payment_methods_details(id):
    return 'hola'

@payments_bp.route('/methods/create')
def payment_methods_create():
    return 'hola'

@payments_bp.route('/methods/<int:id>/edit')
def payment_methods_edit(id):
    return 'hola'



@payments_bp.route('/transactions')
def payment_transactions_list():
    return 'hola'

@payments_bp.route('/transactions/<int:id>')
def payment_transactions_details(id):
    return 'hola'

@payments_bp.route('/transactions/create')
def payment_transactions_create():
    return 'hola'

@payments_bp.route('/transactions/<int:id>/edit')
def payment_transactions_edit(id):
    return 'hola'
