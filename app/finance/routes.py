from flask import render_template, redirect, url_for, request

from . import finance_bp


@finance_bp.route('/finance')
def index():
    title = 'Finanzas'
    prev_url = url_for('public.index')

    return render_template('finance/index.html', 
                           title=title, 
                           prev_url=prev_url)