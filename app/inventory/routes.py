from flask import render_template, redirect, url_for, flash, request

from . import inventory_bp

from .services import WarehouseServices, InventoryService
 
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

    

        

    return render_template('inventory/warehouses/add_warehouse.html',
                           title = title,
                           prev_url = prev_url,
                           form = None,
                           )


#**********************************************************************
#**************************************STOCK**************************
#***********************************************************************


#*****************************stock_materials**************************
@inventory_bp.route('/materials/stock', methods=["GET", "POST"]) 
def view_materials_stock():
    title = 'Materiales'
    prev_url = url_for('inventory.index')

    
    materials = None
     

    return render_template('inventory/material_stock/view_materials_stock.html',
                           title = title,
                           prev_url = prev_url,
                           materials = materials)



@inventory_bp.route('/materials/inventory/<int:material_id>')
def view_material_stock_movements(material_id):
    title = 'Movimientos de inventario'
    prev_url = url_for('inventory.index')
    
    material = None

    return render_template('inventory/materials/view_material_stock_movement.html',
                           title = title,
                           prev_url = prev_url,
                           material = material)


@inventory_bp.route('/materials/entry', methods=['GET', 'POST'])
def add_material_entry():
    title = 'Nuevo Material'
    prev_url = url_for('inventory.view_materials_stock')

    

    return render_template('inventory/material_stock/add_material_entry.html',
                           title = title,
                           prev_url = prev_url,
                           form = None,
                           today = None)


@inventory_bp.route('/materials/exit', methods=['GET', 'POST'])
def add_material_exit():
    title = 'Egreso de materiales'
    prev_url = url_for('inventory.view_materials_stock')

    
         
    return render_template('inventory/material_stock/add_material_exit.html',
                           title = title,
                           prev_url = prev_url,
                           form = None,
                           today = None)


@inventory_bp.route('/massive-stock-upload', methods=['GET', 'POST'])
def massive_stock_upload():
    title = 'Carga masiva'
    prev_url = url_for('inventory.view_materials')
    

    return render_template('inventory/materials/massive_upload.html',
                           title = title,
                           prev_url = prev_url,
                           form = None,
                           errors = None)


#********************************************************************************
#**************************Products*********************************************
#*******************************************************************************

