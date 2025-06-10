from flask import Blueprint, render_template, url_for, redirect, request, flash


materials_bp = Blueprint('materials', __name__, url_prefix='/materials', template_folder='../templates')



@materials_bp.route('/')
def materials_list():
    return render_template('materials/material_list.html')

@materials_bp.route('/<int:id>')
def meterials_detail(id):
    return render_template('materials/material_detail.html', material_id=id)


@materials_bp.route('/create', methods=['GET'])
def create_material_view():
    return render_template('materials/material_create.html')


@materials_bp.route('/<int:id>/edit')
def edit_material(id):
    return render_template('materials/material_edit.html', material_id=id)

  
#***************Lots**********************


@materials_bp.route('/<int:id>/lots')
def materials_lots(id):
    return render_template('materials/material_lots.html', material_id=id)


@materials_bp.route('/lots/<int:id>')
def material_lots_detail(id):
    return render_template('materials/lot_detail.html', lot_id=id)

@materials_bp.route("/lots/create")
def create_lot():
    return render_template("materials/lot_create.html")

@materials_bp.route('/<int:id>/lots/create')
def create_material_lot(id):
    return render_template('materials/lot_create.html', material_id=id)

