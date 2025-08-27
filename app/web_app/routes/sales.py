from flask import Blueprint, render_template, url_for, redirect, request, flash


sales_bp = Blueprint('sales', __name__, url_prefix='/sales', template_folder='../templates')

@sales_bp.route('/approval-criteria')
def approval_criteria():
    return render_template('sales/approval_criteria.html')

@sales_bp.route('/index')
def index():
    return render_template('sales/index.html')


@sales_bp.route('/sale-orders')
def sale_list():
    return render_template('/sales/sale-orders/sale_order_list.html')

@sales_bp.route('/sale-orders/<int:id>')
def sale_detail(id):
    return render_template('sales/sale-orders/sale_order_view.html', order_id=id)

@sales_bp.route('/sale-orders/create', methods=['GET'])
def create_sale_view():
    return render_template('sales/sale-orders/sale_order_create.html')