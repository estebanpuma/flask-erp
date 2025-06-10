from flask import Blueprint, render_template


suppliers_bp = Blueprint('suppliersw', __name__, url_prefix='/suppliers', template_folder='../templates')


@suppliers_bp.route('/')
def suppliers_list():
    return 'hola'

@suppliers_bp.route('/<int:id>')
def suppliers_details(id):
    return 'hola'

@suppliers_bp.route('/create')
def suppliers_create():
    return 'hola'

@suppliers_bp.route('/<int:id>/edit')
def suppliers_edit(id):
    return 'hola'
