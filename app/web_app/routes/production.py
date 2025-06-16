from flask import Blueprint, render_template, url_for, redirect, request, flash


production_bp = Blueprint('production', __name__, url_prefix='/production', template_folder='../templates')


@production_bp.route('/')
def index():
    return render_template('production/index.html')