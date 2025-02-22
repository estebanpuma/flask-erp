from flask import render_template, redirect, url_for, request, flash

from .forms import GrossMarginForm

from .services import PricingServices

from . import pricing_bp


@pricing_bp.route('/pricing', methods=['GET', 'POST'])
def index():
    title = 'Precios'
    prev_url = url_for('finance.index')
    form = GrossMarginForm()
    actual_margin = PricingServices.get_active_gross_margin()
    if form.validate_on_submit():
        PricingServices.create_gross_margin(value= form.value.data,
                                       notes=form.notes.data,
                       )
        flash('Formulario válido', 'success')
    else:
        flash('Formulario inválido', 'danger')


    return render_template('pricing/index.html', 
                           title=title, 
                           prev_url=prev_url,
                           form=form,
                           actual_margin=actual_margin)