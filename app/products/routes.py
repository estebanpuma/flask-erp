from flask import render_template, request, flash, redirect, url_for

from . import products_bp
from .forms import ProductModelForm, ProductLineForm, ProductSubLineForm
from .services import ProductServices


@products_bp.route('/products/index')
def index():
    title = 'Productos'
    prev_url = url_for('production.index')
    return render_template('products/index.html',
                           title = title,
                           prev_url = prev_url)


@products_bp.route('/products')
def view_products():
    title = 'Productos'
    prev_url = url_for('products.index')
    
    products = ProductServices.get_all_products()

    return render_template('products/models/view_products.html',
                           title = title,
                           prev_url = prev_url,
                           products = products)


@products_bp.route('/products/<int:product_id>')
def view_product(product_id):
    title = 'Producto'
    prev_url = url_for('products.view_products')
    
    return render_template('products/models/view_product.html',
                           title = title,
                           prev_url = prev_url)


@products_bp.route('/products/create', methods=['GET', 'POST'])
def add_product():
    title = 'Producto'
    prev_url = url_for('products.view_products')
    form = ProductModelForm()
    line_form = ProductLineForm(prefix='line')
    subline_form = ProductSubLineForm(prefix='subline')

    if form.validate_on_submit() and form.submit.data:
        flash(form.data)
    if line_form.validate_on_submit() and form.submit.data:
        flash(line_form.data)
    else:
        flash(form.errors)
    return render_template('products/models/add_product.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           line_form = line_form,
                           subline_form = subline_form)


@products_bp.route('/products/<int:product_id>/put', methods=['GET', 'POST'])
def edit_product(product_id):
    title = 'Producto'
    prev_url = url_for('products.view_products')
    
    return render_template('products/models/add_product.html',
                           title = title,
                           prev_url = prev_url)


#*******************************************************************
#************************Linea de productos**************************
#********************************************************************

@products_bp.route('/lines')
def view_lines():
    title = 'Lineas'
    prev_url = url_for('products.index')
    
    lines = ProductServices.get_all_lines()

    return render_template('products/lines/view_lines.html',
                           title = title,
                           prev_url = prev_url,
                           lines = lines)


@products_bp.route('/lines/<int:line_id>')
def view_line(line_id):
    title = 'Linea'
    prev_url = url_for('products.view_lines')
    line = ProductServices.get_line(line_id)
    
    return render_template('products/lines/view_linesub.html',
                           title = title,
                           prev_url = prev_url,
                           line = line)


@products_bp.route('/lines/create', methods=['GET', 'POST'])
def add_line():
    title = 'Nueva Linea'
    prev_url = url_for('products.view_lines')
    form = ProductLineForm()

    if form.validate_on_submit():
        flash(form.data)
    
    return render_template('products/lines/add_line.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)


@products_bp.route('/lines/<int:line_id>/put', methods=['GET', 'POST'])
def edit_line(line_id):
    title = 'Editar Linea'
    prev_url = url_for('products.view_lines')
    
    return render_template('products/lines/add_line.html',
                           title = title,
                           prev_url = prev_url)


#*******************************************************************
#************************SubLinea de productos**************************
#********************************************************************

@products_bp.route('/sublines')
def view_sublines():
    title = 'subLineas'
    prev_url = url_for('products.index')
    
    sublines = ProductServices.get_all_sublines()

    return render_template('products/sublines/view_sublines.html',
                           title = title,
                           prev_url = prev_url,
                           sublines = sublines)


@products_bp.route('/sublines/<int:subline_id>')
def view_subline(subline_id):
    title = 'SubLinea'
    prev_url = url_for('products.view_sublines')
    subline = ProductServices.get_subline(subline_id)
    
    return render_template('products/sublines/view_subline.html',
                           title = title,
                           prev_url = prev_url,
                           subline = subline)


@products_bp.route('/sublines/create', methods=['GET', 'POST'])
def add_subline():
    title = 'Nueva SubLinea'
    prev_url = url_for('products.view_sublines')
    form = ProductSubLineForm()

    if form.validate_on_submit():
        flash(form.data)
    
    return render_template('products/sublines/add_subline.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)


@products_bp.route('/sublines/<int:subline_id>/put', methods=['GET', 'POST'])
def edit_subline(subline_id):
    title = 'Editar SubLinea'
    prev_url = url_for('products.view_sublines')
    
    return render_template('products/sublines/add_subline.html',
                           title = title,
                           prev_url = prev_url)