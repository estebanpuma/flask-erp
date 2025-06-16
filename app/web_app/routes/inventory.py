from flask import Blueprint, render_template, url_for, redirect, request, flash


inventory_bp = Blueprint('winventory', __name__, url_prefix='/inventory', template_folder='../templates')



@inventory_bp.route('/')
def index():
    return render_template('inventory/index.html')