from flask import Blueprint, render_template

materials_bp = Blueprint('materials', __name__, url_prefix='/materials', template_folder='../templates')

@materials_bp.route('/')
def materials_list():
    return render_template('materials/list.html')