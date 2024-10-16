from flask import render_template, redirect, url_for, flash

from . import production_bp

@production_bp.route('/production/index')
def index():
    title = 'production'
    prev_url = url_for('public.index')
    return render_template('production/index.html',
                           title = title,
                           prev_url = prev_url)

