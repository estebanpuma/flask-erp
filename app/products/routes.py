from flask import render_template, request, flash, redirect, url_for, jsonify

from . import products_bp
from .forms import ProductModelForm, ProductLineForm, ProductSubLineForm, ColorForm, SerieForm
from .services import ProductServices, ColorServices, LineServices, SublineServices, SeriesServices

import pandas as pd
import io


@products_bp.route('/models/index')
def index():
    title = 'Modelos'
    prev_url = url_for('production.index')
    return render_template('products/index.html',
                           title = title,
                           prev_url = prev_url)


@products_bp.route('/products')
def view_products():
    title = 'Modelos'
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
                           prev_url = prev_url,
                           product_id = product_id)


@products_bp.route('/products/create', methods=['GET', 'POST'])
def add_product():
    title = 'Nuevo Modelo'
    prev_url = url_for('products.view_products')
    form = ProductModelForm()

    
    if form.validate_on_submit():
        
        from .services import ProductServices
        try:
            new_product = ProductServices.create_product(line_id=form.line_id.data,
                                                        subline_id=form.subline_id.data,
                                                        code= form.code.data,
                                                        colors=form.colors.data,
                                                        name= form.name.data,
                                                        description= form.description.data,
                                                        items = form.items.data,
                                                        images = form.images.data)
            flash('Modelo guardado', 'success')
            return redirect(url_for('products.view_products'))
        
        except Exception as e:
            flash('No se pudo guardar el modelo.', 'danger')
    
    flash(form.errors)
    form_colors = [{'id':color['color']} for color in form.colors.data]
    form_items = [{'code':item['code'], 'qty':item['qty'], 'serie':['serie']} for item in form.items.data]
    form_data = {
        'code': form.code.data,
        'line': form.line_id.data,
        'name': form.name.data,
        'subline': form.subline_id.data,
        'colors': form_colors,
        'items': form_items,
        'description': form.description.data
    }
    
    return render_template('products/models/add_product.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           form_data = form_data)
                           


@products_bp.route('/products/massive_upload/create', methods=['GET', 'POST'])
def add_product_massive_upload():
    title = 'Carga Masiva'
    prev_url = url_for('products.view_products')

    return render_template('products/models/add_product_massive_upload.html',
                           title = title,
                           prev_url = prev_url)



@products_bp.route('/products/<int:product_id>/put', methods=['GET', 'POST'])
def edit_product(product_id):
    title = 'Producto'
    prev_url = url_for('products.view_products')

    product = ProductServices.get_product(product_id)

    form = ProductModelForm()

    obj_colors = [{'id':color.color_id} for color in product.colors]
    obj_items = product.material_details
    obj_items = [{'material_id':item.material_id, 'qty':item.quantity, 'serie_id':item.serie_id} for item in obj_items]
    
        
    print('items: ',obj_items)
    obj_images = [{'id':image.id, 'url':image.image_path} for image in product.images]
    obj_data = {
        'code': product.code,
        'line': product.line_id,
        'name': product.name,
        'subline': product.sub_line_id,
        'colors': obj_colors,
        'items': obj_items,
        'images': obj_images,
        'description': product.description
    } 
   
    if form.validate_on_submit():
        try:
            ProductServices.update_product(product_id, line_id=form.line_id.data,
                                           subline_id=form.subline_id.data,
                                           code=form.code.data,
                                           colors=form.colors.data,
                                           description=form.description.data,
                                           items=form.items.data,
                                           images=form.images.data)
            return redirect(url_for('products.view_product', product_id=product_id))
        except Exception as e:
            flash('No se pudo guardar el modelo.', 'danger')
    
    return render_template('products/models/edit_product.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           form_data = obj_data)


@products_bp.route('/products/<int:product_id>/delete')
def delete_product(product_id):
    try:
        ProductServices.delete_product(product_id)
        flash('Registro eliminado', 'success')
        return redirect(url_for('products.view_products'))
    except Exception as e:
        flash(str(e), 'danger')
        raise ValueError('No se pude eliminar le registro')
#*******************************************************************
#************************Linea de productos**************************
#********************************************************************

@products_bp.route('/lines')
def view_lines():
    title = 'Lineas'
    prev_url = url_for('products.index')
    
    lines = LineServices.get_all_lines()

    return render_template('products/lines/view_lines.html',
                           title = title,
                           prev_url = prev_url,
                           lines = lines)


@products_bp.route('/lines/<int:line_id>')
def view_line(line_id):
    title = 'Linea'
    prev_url = url_for('products.view_lines')
    line = LineServices.get_line(line_id)
    
    return render_template('products/lines/view_line.html',
                           title = title,
                           prev_url = prev_url,
                           line = line)


@products_bp.route('/lines/create', methods=['GET', 'POST'])
def add_line():
    title = 'Nueva Linea'
    prev_url = url_for('products.view_lines')
    line_form = ProductLineForm()

    if line_form.validate_on_submit():
        try:
            new_line = LineServices.create_line(line_form.code.data,
                                              line_form.name.data,
                                              line_form.description.data)
            return redirect(url_for('products.view_lines'))
        except Exception as e:
            flash(f'Ocurrio un error: {e}')
    
    return render_template('products/lines/add_line.html',
                           title = title,
                           prev_url = prev_url,
                           line_form = line_form)


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
    
    sublines = SublineServices.get_all_sublines()

    return render_template('products/sublines/view_sublines.html',
                           title = title,
                           prev_url = prev_url,
                           sublines = sublines)


@products_bp.route('/sublines/<int:subline_id>')
def view_subline(subline_id):
    title = 'SubLinea'
    prev_url = url_for('products.view_sublines')
    subline = SublineServices.get_subline(subline_id)
    
    return render_template('products/sublines/view_subline.html',
                           title = title,
                           prev_url = prev_url,
                           subline = subline)


@products_bp.route('/sublines/create', methods=['GET', 'POST'])
def add_subline():
    title = 'Nueva SubLinea'
    prev_url = url_for('products.view_sublines')
    subline_form = ProductSubLineForm()

    if subline_form.validate_on_submit():
        try:
            new_subline = SublineServices.create_subline(subline_form.code.data,
                                              subline_form.name.data,
                                              subline_form.description.data)
            return redirect(url_for('products.view_sublines'))
        except Exception as e:
            flash(f'Ocurrio un error: {e}')
    
    return render_template('products/sublines/add_subline.html',
                           title = title,
                           prev_url = prev_url,
                           subline_form = subline_form)


@products_bp.route('/sublines/<int:subline_id>/put', methods=['GET', 'POST'])
def edit_subline(subline_id):
    title = 'Editar SubLinea'
    prev_url = url_for('products.view_sublines')
    
    return render_template('products/sublines/add_subline.html',
                           title = title,
                           prev_url = prev_url)


#*************************************************************************
#**********************************Colores*******************************

@products_bp.route('/model_colors')
def view_model_colors():
    title = 'Colores'
    prev_url = url_for('products.index')
    colors = ColorServices.get_all_colors()

    return render_template('products/colors/view_model_colors.html',
                           title = title,
                           prev_url = prev_url,
                           colors = colors)


@products_bp.route('/model_colors/<int:model_color_id>')
def view_model_color(model_color_id):
    title = 'Color'
    prev_url = url_for('products.view_model_colors')
    color = ColorServices.get_color(model_color_id)

    return render_template('products/colors/view_model_color.html',
                           title = title,
                           prev_url = prev_url,
                           color = color)


@products_bp.route('/model_colors/create', methods=['GET', 'POST'])
def add_model_color():
    title = 'Colores'
    prev_url = url_for('products.view_model_colors')
    form = ColorForm()

    if form.validate_on_submit():
        try:
            new_color = ColorServices.create_color(code=form.code.data,
                                               name=form.name.data,
                                               hex=form.hex.data,
                                               description=form.description.data)
            return redirect(url_for('products.view_model_colors'))
        except Exception as e:
            flash('Ocurrio un error', 'danger')

    return render_template('products/colors/add_model_color.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)


@products_bp.route('/model_colors/<int:model_color_id>/update')
def update_model_color(model_color_id):
    title = 'Editar Colores'
    prev_url = url_for('products.view_model_colors')
    model_color = ColorServices.get_color(model_color_id)
    form = ColorForm(obj=model_color)

    if form.validate_on_submit():
        flash(form.data)

    return render_template('products/colors/update_model_color.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)



#*************************************************************************
#**********************************Series*******************************

@products_bp.route('/products/series')
def view_series():
    title = 'Series'
    prev_url = url_for('products.index')
    series = SeriesServices.get_all_series()

    return render_template('products/series/view_series.html',
                           title = title,
                           prev_url = prev_url,
                           series = series)


@products_bp.route('/product/series/<int:serie_id>')
def view_serie(serie_id):
    title = 'Serie'
    prev_url = url_for('products.view_series')
    serie = SeriesServices.get_serie(serie_id)

    return render_template('products/series/view_serie.html',
                           title = title,
                           prev_url = prev_url,
                           serie = serie)


@products_bp.route('/products/series/create', methods=['GET', 'POST'])
def add_serie():
    title = 'Nueva Serie'
    prev_url = url_for('products.view_series')
    form = SerieForm()

    if form.validate_on_submit():
        
        try:
            new_serie = SeriesServices.create_serie(name=form.name.data,
                                                    start_size=form.start_size.data,
                                                    end_size=form.end_size.data,
                                                    description=form.description.data)
            
            flash(f'Serie{form.name.data} guardada', 'success')
            return redirect(url_for('products.view_series'))
        except Exception as e:
            flash(f'Ocurrio un error{e}', 'danger')

    return render_template('products/series/add_serie.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)


@products_bp.route('/products/series/<int:serie_id>/update', methods=['GET', 'POST'])
def update_serie(serie_id):
    title = 'Editar Colores'
    prev_url = url_for('products.view_series')
    serie = SeriesServices.get_serie(serie_id)
    form = SerieForm(obj=serie)

    if form.validate_on_submit():
        flash(form.data)

    return render_template('products/series/add_serie.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)


@products_bp.route('/products/series/<int:serie_id>/delete')
def delete_serie(serie_id):
    try:
        serie = SeriesServices.delete_serie(serie_id)
        return redirect(url_for('products.view_series'))
    except Exception:
        flash('Ocurrio un error. No se puede borrar registro')
        raise ValueError('Ocurrio un error. No se puede borrar registro')
