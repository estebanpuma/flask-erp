from flask import Blueprint, render_template, url_for, redirect, request, flash


products_bp = Blueprint('products', __name__, url_prefix='/products', template_folder='../templates')


@products_bp.route('/')
def product_list():
    return render_template('/products/product_list.html')

@products_bp.route('/<int:id>')
def product_detail(id):
    return render_template('products/product_detail.html', product_id=id)


@products_bp.route('/create', methods=['GET'])
def create_product_view():
    return render_template('products/product_wizard.html')