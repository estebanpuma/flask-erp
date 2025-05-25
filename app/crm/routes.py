from flask import render_template, redirect, url_for, flash


from .services import CRMServices

from . import crm_bp


@crm_bp.route('/crm/index')
def index():
    title = 'CRM'
    prev_url = url_for('sales.index')

    return render_template('crm/index.html',
                           title = title,
                           prev_url = prev_url)



@crm_bp.route('/clients')
def view_clients():
    title = 'Clientes'
    prev_url = url_for('crm.index')
    clients = CRMServices.get_all_clients()

    return render_template('crm/view_clients.html',
                           title = title,
                           prev_url = prev_url,
                           clients = clients)


@crm_bp.route('/clients/<int:client_id>')
def view_client(client_id):
    title = 'Cliente'
    prev_url = url_for('crm.view_clients')

    client = CRMServices.get_client(client_id)

    return render_template('crm/view_client.html',
                           title = title,
                           prev_url = prev_url,
                           client = client)


@crm_bp.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    title = 'Crear Cliente'
    prev_url = url_for('crm.view_clients')
    data=None

    form = None
        
        

    return render_template('crm/add_client.html',
                           title = title,
                           prev_url = prev_url,
                           form = form,
                           data=data)


@crm_bp.route('/clients/<int:client_id>/update')
def update_client(client_id):
    return render_template('crm/update_client.html', client_id=client_id)


@crm_bp.route('/crm/provinces')
def view_provinces():
    title = 'Provincias'
    prev_url = url_for('crm.index')

    from .services import LocationsServices

    provinces = LocationsServices.get_provinces()

    return render_template('crm/view_provinces.html',
                           title = title,
                           prev_url = prev_url,
                           provinces = provinces)


@crm_bp.route('/crm/provinces/<int:province_id>')
def view_province(province_id):
    title = 'Provincia'
    prev_url = url_for('crm.view_provinces')
    province_id = int(province_id)

    return render_template('crm/view_province.html',
                           title = title,
                           prev_url = prev_url,
                           province_id =province_id)


@crm_bp.route('/crm/provinces/add')
def add_province():
    title = 'Crear Provincia'
    prev_url = url_for('crm.view_provinces')

    return render_template('crm/add_province.html',
                           title = title,
                           prev_url = prev_url)



@crm_bp.route('/crm/cities')
def view_cities():
    title = 'Ciudades'
    prev_url = url_for('crm.index')

    return render_template('crm/view_cities.html',
                           title = title,
                           prev_url = prev_url)





@crm_bp.route("/test/upload-materials")
def upload_materials_form():
    return render_template("upload_clients_bulk.html")
