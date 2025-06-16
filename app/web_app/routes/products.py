from flask import Blueprint, render_template, url_for, redirect, request, flash


products_bp = Blueprint('products', __name__, url_prefix='/products', template_folder='../templates')


@products_bp.route('/index')
def product_index():
    return render_template('/products/index.html')

@products_bp.route('/')
def product_list():
    return render_template('/products/product_list.html')

@products_bp.route('/<int:id>')
def product_detail(id):
    return render_template('products/product_detail.html', product_id=id)

@products_bp.route('/create', methods=['GET'])
def create_product_view():
    return render_template('products/product_wizard.html')


#----------------------------------------------------
#------------------------DEsigns--------------------

@products_bp.route('/desings')
def design_list():
    return render_template('/products/designs/design_list.html')

@products_bp.route('/designs/<int:id>')
def design_detail(id):
    return render_template('products/designs/design_detail.html', design_id=id)

@products_bp.route('/designs/create', methods=['GET'])
def create_design_view():
    return render_template('products/product_wizard.html')


#----------------------------------------------------
#------------------------Variants--------------------

@products_bp.route('/variants')
def variant_list():
    return render_template('/products/variants/variant_list.html')

@products_bp.route('/variants/<int:id>')
def variant_detail(id):
    return render_template('products/variants/variant_detail.html', variant_id=id)

@products_bp.route('/variants/create', methods=['GET'])
def create_variant_view():
    return render_template('products/product_wizard.html')


#-------------------------------------------------------
#------------------Lines---------------------------
@products_bp.route('/lines/create', methods=['GET'])
def create_line():
    return render_template('products/lines/line_create.html')


@products_bp.route('/lines')
def product_line_list():
    return render_template('/products/lines/line_list.html')

@products_bp.route('/lines/<int:id>')
def product_line_detail(id):
    return render_template('products/lines/line_detail.html', line_id=id)



#-------------------------------------------------------
#------------------SubLines---------------------------
@products_bp.route('/sublines/create', methods=['GET'])
def create_subline():
    return render_template('products/sublines/subline_create.html')


@products_bp.route('/sublines')
def product_subline_list():
    return render_template('products/sublines/subline_list.html')

@products_bp.route('/sublines/<int:id>')
def product_subline_detail(id):
    return render_template('products/sublines/subline_detail.html', subline_id=id)



#-------------------------------------------------------
#------------------Collections--------------------------
@products_bp.route('/collections/create', methods=['GET'])
def create_collection():
    return render_template('products/collections/collection_create.html')


@products_bp.route('/collections')
def product_collection_list():
    return render_template('/products/collections/collection_list.html')

@products_bp.route('/collections/<int:id>')
def product_collection_detail(id):
    return render_template('products/collections/collection_detail.html', collection_id=id)
