from flask import render_template, redirect, url_for, flash

from .services import MaterialServices

from . import materials_bp


#****************************Materiales/*************************

@materials_bp.route('/material-groups', methods=["GET", "POST"]) 
def view_material_groups():
    title = 'Grupos de materiales'
    prev_url = url_for('inventory.index')

    groups = None
    
    return render_template('inventory/materials/view_material_groups.html',
                           title = title,
                           prev_url = prev_url,
                           groups = groups)


@materials_bp.route('/material-groups/<int:group_id>', methods=["GET", "POST"]) 
def view_material_group(group_id):
    title = 'Grupo'
    prev_url = url_for('inventory.view_material_groups')

    group = None
    
    return render_template('inventory/materials/view_material_group.html',
                           title = title,
                           prev_url = prev_url,
                           group = group)


@materials_bp.route('/material-groups/create', methods=["GET", "POST"]) 
def add_material_group():
    title = 'Nuevo grupo de materiales'
    prev_url = url_for('inventory.view_material_groups')
    form = None
    
        
    
    return render_template('inventory/materials/add_material_group.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)


@materials_bp.route('/material-groups/<int:group_id>/update', methods=["GET", "POST"]) 
def update_material_group(group_id):
    title = 'Editar grupo'
    

    return render_template('inventory/materials/add_material_group.html',
                           title = title,
                           )


@materials_bp.route('/materials', methods=["GET", "POST"]) 
def view_materials():
    title = 'Materiales'
    prev_url = url_for('inventory.index')

    
    materials = None
    
    return render_template('inventory/materials/view_materials.html',
                           title = title,
                           prev_url = prev_url,
                           materials = materials)


@materials_bp.route('/materials/<int:material_id>')
def view_material(material_id):
    title = 'Materiales'
    prev_url = url_for('inventory.view_materials_stock')
    
    material = MaterialServices.get_material(material_id)
    movements = None
    print(movements)
    return render_template('inventory/materials/view_material.html',
                           title = title,
                           prev_url = prev_url,
                           material = material,
                           movements = movements)


@materials_bp.route('/materials/create', methods=['GET', 'POST'])
def add_material():
    title = 'Nuevo Material'
    prev_url = url_for('inventory.view_materials')

    form = None
       

    return render_template('inventory/materials/add_material.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)


@materials_bp.route('/materials/<int:material_id>/update', methods=['GET', 'POST'])
def update_material(material_id):
    title = 'Nuevo Material'
    material = MaterialServices.get_material(material_id)
    prev_url = url_for('inventory.view_materials')

    form = None
       

    return render_template('inventory/materials/add_material.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)



@materials_bp.route('/materials/bulk/create', methods=['GET', 'POST'])
def add_bulk_materials():
    title = 'Carga masiva'
    prev_url = url_for('inventory.view_materials')
    errors = None

    

    return render_template('inventory/materials/massive_upload.html',
                           title = title,
                           prev_url = prev_url,
                           errors = errors)


@materials_bp.route("/test/upload-materials")
def upload_materials_form():
    return render_template("upload_materials_bulk.html")
