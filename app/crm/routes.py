from flask import render_template, redirect, url_for, flash

from .forms import ClientForm
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

    form = ClientForm()

    if form.validate_on_submit():

        new_client = CRMServices.create_client(ruc_or_ci = form.ruc_or_ci.data,
                                               client_type = form.client_type.data,
                                               name = form.name.data,
                                               city = form.city.data,
                                               address = form.address.data,
                                               phone = form.phone.data,
                                               email = form.email.data)
        
        return redirect(url_for('crm.view_clients'))

    return render_template('crm/add_client.html',
                           title = title,
                           prev_url = prev_url,
                           form = form)