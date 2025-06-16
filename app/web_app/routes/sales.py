from flask import Blueprint, render_template, url_for, redirect, request, flash


sales_bp = Blueprint('sales', __name__, url_prefix='/sales', template_folder='../templates')



@sales_bp.route('/index')
def index():
    return render_template('sales/index.html')