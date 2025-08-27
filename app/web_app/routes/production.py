from flask import Blueprint, render_template, url_for, redirect, request, flash


production_bp = Blueprint('production', __name__, url_prefix='/production', template_folder='../templates')


@production_bp.route('/')
def index():
    return render_template('production/index.html')


@production_bp.route('/resources/create')
def production_resources_create():
    return render_template('production/resources/create.html')

@production_bp.route('/resources')
def production_resources_list():
    return render_template('production/resources/list.html')


@production_bp.route('/resources/<int:id>')
def production_resources_detail(id):
    return render_template('production/resources/detail.html', id=id)


@production_bp.route('/resources/<int:id>/edit')
def production_resources_edit(id):
    return render_template('production/resources/edit.html', id=id)



@production_bp.route('/operations')
def operations_list():
    return render_template('operations/list.html')


@production_bp.route('/operations/<int:id>')
def operations_detail(id):
    return render_template('operations/detail.html', id=id)


@production_bp.route('/operations/create')
def operations_create():
    return render_template('operations/create.html')



#------------------Capacidad instalada/Capacity-----------------------------------------
@production_bp.route('/capacity')
def capacity_index():
    return render_template('production/capacity/index.html')

@production_bp.route('/operations-sheet/create', methods=['GET', 'POST'])
def operation_sheet_create():
    return render_template('operations/operations_sheet_create.html')

@production_bp.route('/operations-sheet/<int:id>')
def operation_sheet_detail():
    return render_template('operations/operations_sheet_detail.html')

@production_bp.route('/operations-sheet')
def operation_sheet_list():
    return render_template('operations/operations_sheet_list.html')


@production_bp.route('/setup')
def setup():
    return render_template('production/setup_wizard.html')