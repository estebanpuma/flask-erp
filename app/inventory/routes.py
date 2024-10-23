from flask import render_template, redirect, url_for, flash, request

from . import inventory_bp
from .forms import MaterialForm, WarehouseForm, MaterialEntryForm, MaterialExitForm
from .services import MaterialServices, WarehouseServices, InventoryService
 
import pandas as pd

import io


@inventory_bp.route('/inventory/index')
def index():
    title = 'Inventario'
    prev_url = url_for('public.index')

    return render_template('inventory/index.html',
                            title = title,
                            prev_url = prev_url)


@inventory_bp.route('/warehouse')
def warehouse():
    title = 'Bodegas'
    prev_url = url_for('inventory.warehouse')

    return 'Bodegass'



@inventory_bp.route('/materials', methods=["GET", "POST"]) 
def view_materials():
    title = 'Materiales'
    prev_url = url_for('inventory.index')

    
    materials = MaterialServices.get_all_materials()
    
    

    return render_template('inventory/materials/view_materials.html',
                           title = title,
                           prev_url = prev_url,
                           materials = materials)



@inventory_bp.route('/materials/<int:material_id>')
def view_material(material_id):
    title = 'Materiales'
    prev_url = url_for('inventory.view_materials_stock')
    
    material = MaterialServices.get_material(material_id)
    movements = InventoryService.get_item_movementsNew('RAWMATERIAL', material.code)
    print(movements)
    return render_template('inventory/materials/view_material.html',
                           title = title,
                           prev_url = prev_url,
                           material = material,
                           movements = movements)


@inventory_bp.route('/materials/create', methods=['GET', 'POST'])
def add_material():
    title = 'Nuevo Material'
    prev_url = url_for('inventory.view_materials')

    form = MaterialForm()

    if form.validate_on_submit():
        try: 
            new_material = MaterialServices.create_material(code = form.code.data,
                                                        name = form.name.data,
                                                        description = form.description.data,
                                                        unit = form.unit.data)
            flash('Registro guardado!', 'success')
            return redirect(url_for('inventory.view_materials'))
        
        except Exception as e:
            flash(f'Ocurrio un error: {e}')
            return redirect(url_for('inventory.view_materials'))

        

    return render_template('inventory/materials/add_material.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)


@inventory_bp.route('/massive-upload', methods=['GET', 'POST'])
def massive_upload():
    title = 'Carga masiva'
    prev_url = url_for('inventory.view_materials')
    from ..common.forms import MasiveUploadFileForm

    form = MasiveUploadFileForm()
    errors = None

    if form.validate_on_submit():
        file = form.file.data
        file_extension = file.filename.split('.')[-1]

        from ..common.utils import process_file_data
        from ..products.models import Material
        if file_extension == 'csv':
            df = pd.read_csv(file)
        else:
            file_contents = file.read()  # Lee el archivo en memoria
            df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl')
        flash(df.columns)
        columns = ['code', 'name', 'description', 'unit']
        data = process_file_data(df, Material, columns)
        
        if data['errors']:
           flash(data['message'], 'warning')
           errors = data['errors']
           return render_template('inventory/materials/massive_upload.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           errors = errors)
        else:
            flash('El archivo se cargó exitosamente.', 'success')
            return redirect('inventory.view_materials')

    return render_template('inventory/materials/massive_upload.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           errors = errors)


#**********************************************************************
#*********************Bodegas/Warehouse********************************
#**********************************************************************

@inventory_bp.route('/warehouses', methods=["GET", "POST"]) 
def view_warehouses():
    title = 'Bodegas'
    prev_url = url_for('inventory.index')

    
    warehouses = WarehouseServices.get_all_warehouses()
    
    

    return render_template('inventory/warehouses/view_warehouses.html',
                           title = title,
                           prev_url = prev_url,
                           warehouses = warehouses)



@inventory_bp.route('/warehouses/<int:warehouse_id>')
def view_warehouse(warehouse_id):
    title = 'Bodegas'
    prev_url = url_for('inventory.index')
    
    warehouse = WarehouseServices.get_warehouse(warehouse_id)

    return render_template('inventory/warehouses/view_warehouse.html',
                           title = title,
                           prev_url = prev_url,
                           warehouse = warehouse)


@inventory_bp.route('/warehouses/create', methods=['GET', 'POST'])
def add_warehouse():
    title = 'Nuevo Material'
    prev_url = url_for('inventory.view_warehouses')

    form = WarehouseForm()

    if form.validate_on_submit():
        try: 
            new_warehouse = WarehouseServices.create_warehouse(code = form.code.data,
                                                        name = form.name.data,
                                                        description = form.description.data,
                                                        location = form.location.data)
            flash('Registro guardado!', 'success')
            return redirect(url_for('inventory.view_warehouses'))
        
        except Exception as e:
            flash(f'Ocurrio un error: {e}')
            return redirect(url_for('inventory.view_warehouses'))

        

    return render_template('inventory/warehouses/add_warehouse.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           )


#**********************************************************************
#**************************************STOCK**************************
#***********************************************************************


#*****************************stock_materials**************************
@inventory_bp.route('/materials/stock', methods=["GET", "POST"]) 
def view_materials_stock():
    title = 'Materiales'
    prev_url = url_for('inventory.index')

    
    materials = MaterialServices.get_all_materials() 
     

    return render_template('inventory/material_stock/view_materials_stock.html',
                           title = title,
                           prev_url = prev_url,
                           materials = materials)



@inventory_bp.route('/materials/inventory/<int:material_id>')
def view_material_stock_movements(material_id):
    title = 'Movimientos de inventario'
    prev_url = url_for('inventory.index')
    
    material = MaterialServices.get_material(material_id)

    return render_template('inventory/materials/view_material_stock_movement.html',
                           title = title,
                           prev_url = prev_url,
                           material = material)


@inventory_bp.route('/materials/entry', methods=['GET', 'POST'])
def add_material_entry():
    title = 'Nuevo Material'
    prev_url = url_for('inventory.view_materials_stock')

    form = MaterialEntryForm()
    from ..common.utils import get_today
    today = get_today()

    if form.validate_on_submit():

        
        new_entry = InventoryService.create_material_entry(movement_trigger=form.movement_trigger.data,
                                                          date= form.date.data,
                                                          responsible=form.responsible.data,
                                                          warehouse=form.warehouse.data,
                                                          document=form.document.data,
                                                          items=form.items.data
                                                          )
        
        if new_entry:
           flash(f'Registro guardado', 'success')
           return redirect(url_for('inventory.view_materials_stock'))
        else:
            flash('Ocurrio un error', 'danger')

    return render_template('inventory/material_stock/add_material_entry.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           today = today)


@inventory_bp.route('/materials/exit', methods=['GET', 'POST'])
def add_material_exit():
    title = 'Egreso de materiales'
    prev_url = url_for('inventory.view_materials_stock')

    form = MaterialExitForm()

    from ..common.utils import get_today
    today = get_today()

    if form.validate_on_submit():
        
       new_exit = InventoryService.create_material_exit(movement_trigger=form.movement_trigger.data,
                                                        date=form.date.data,
                                                        responsible=form.responsible.data,
                                                        warehouse=form.warehouse.data,
                                                        items=form.items.data,
                                                        document=form.document.data)
       if new_exit:
           flash(f'Registro guardado', 'success')
           return redirect(url_for('inventory.view_materials_stock'))
       else:
          
        flash('Ocurrio un error', 'danger')
         
    return render_template('inventory/material_stock/add_material_exit.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           today = today)


@inventory_bp.route('/massive-stock-upload', methods=['GET', 'POST'])
def massive_stock_upload():
    title = 'Carga masiva'
    prev_url = url_for('inventory.view_materials')
    from ..common.forms import MasiveUploadFileForm

    form = MasiveUploadFileForm()
    errors = None

    if form.validate_on_submit():
        file = form.file.data
        file_extension = file.filename.split('.')[-1]

        from ..common.utils import process_file_data
        from ..products.models import Material
        if file_extension == 'csv':
            df = pd.read_csv(file)
        else:
            file_contents = file.read()  # Lee el archivo en memoria
            df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl')
        flash(df.columns)
        columns = ['code','name', 'description', 'unit']
        data = process_file_data(df=df, objModel=Material, expected_columns= columns)
        
        if data['errors']:
           flash(data['message'], 'warning')
           errors = data['errors']
           return render_template('inventory/materials/massive_upload.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           errors = errors)
        else:
            flash('El archivo se cargó exitosamente.', 'success')
            return redirect('inventory.view_materials')

    return render_template('inventory/materials/massive_upload.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           errors = errors)


#********************************************************************************
#**************************Products*********************************************
#*******************************************************************************

@inventory_bp.route('/products/stock')
def view_products_stock():
    title = 'Stock Productos'
    prev_url = url_for('inventory.index')

    from ..products import Product
    from ..products.services import ProductServices

    products = ProductServices.get_all_products()

    return 'products'


@inventory_bp.route('/products/entry')
def add_products_entry():
    title = 'Ingreso Productos'
    prev_url = url_for('inventory.view_products_stock')



    

    return 'products'