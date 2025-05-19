from flask import render_template, redirect, url_for, current_app, flash, request
from flask_login import login_required


from .services import AdminServices
from . import admin_bp


from app import db

@admin_bp.route('/users')
def view_users():
    title = 'Usuarios'
    prev_url = url_for('public.index')

    users = AdminServices.get_all_users()


    return render_template('admin/view_users.html',
                           title = title,
                           prev_url = prev_url,
                           users = users)


@admin_bp.route('/users/<int:user_id>')
def view_user(user_id):
    title = 'Usuario'
    prev_url = url_for('admin.view_users')

    user = AdminServices.get_user(user_id)


    return render_template('admin/view_user.html',
                           title = title,
                           prev_url = prev_url,
                           user = user)


@admin_bp.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    title = 'Editar usuario'
    prev_url = url_for('admin.view_users')

    user = AdminServices.get_user(user_id)


    return render_template('admin/view_user.html',
                           title = title,
                           prev_url = prev_url,
                           user = user)



@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    title = 'Nuevo Usuario'
    prev_url = url_for('admin.view_users')
    form = None
        

    return render_template('admin/add_user.html',
                           title = title,
                           form = form,
                           job_form = None,
                           prev_url = prev_url)



#********************Roles section******************#
@admin_bp.route('/roles')
def view_roles():
    title = 'Roles'
    prev_url = url_for('public.index')
    roles= AdminServices.get_all_roles()

    return render_template('admin/view_roles.html',
                           title = title,
                           roles = roles,
                           prev_url = prev_url)


@admin_bp.route('/roles/<int:role_id>')
def view_role(role_id):
    title = 'Roles'
    prev_url = url_for('admin.view_roles')
    role= AdminServices.get_role(role_id)
    users_with_role = AdminServices.get_users_with_role(role_id)

    return render_template('admin/view_role.html',
                           title = title,
                           role = role,
                           users = users_with_role,
                           prev_url = prev_url)


@admin_bp.route('/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():
    title = 'Nuevo rol'
    prev_url = url_for('admin.view_roles')
    form = None

    return render_template('admin/add_role.html',
                           title = title,
                           form = form,
                           prev_url = prev_url)


@admin_bp.route('/roles/<int:role_id>/edit')
def edit_role(role_id):
    title = 'Roles'
    prev_url = url_for('admin.view_role', role_id=role_id)
    role= AdminServices.get_role(role_id)

    return render_template('admin/view_role.html',
                           title = title,
                           role = role,
                           prev_url = prev_url)


@admin_bp.route('/roles/<int:user_id>/assign', methods=['GET', 'POST'])
def assign_roles(user_id):
    title = 'Asignar roles'
    
    user = AdminServices.get_user(user_id)

    if user is None:
        flash('Ocurrio un error', 'danger')
        return redirect('admin.view_users')
    prev_url = url_for('admin.view_user', user_id=user_id)

    from .models import Role
    roles = Role.query.all()  # Consulta para obtener todos los roles

    form = None
    user_roles = [{ 'name': role.name, 'code':role.code} for role in user.roles]
    

    if form.validate_on_submit():
        # Aquí puedes iterar sobre los roles seleccionados

        selected_roles = request.form.getlist('roles')
        
        new_roles = AdminServices.update_roles(user_id, selected_roles)

        return redirect(url_for('admin.view_user', user_id=user.id))

        # Procesar el resto de la lógica del formulario

    return render_template('admin/assign_roles.html', 
                           title = title,
                           prev_url = prev_url,
                           user_roles = user_roles,
                           roles = roles,
                           form = form)


#********************** Jobs section************************************#

@admin_bp.route('/jobs')
def view_jobs():
    print('entra a jobs')
    title = 'Cargos'
    prev_url = url_for('public.index')
    jobs= AdminServices.get_all_jobs()
    
    #variable para obtener el total de usuarios por cargo/puesto de trabajo
    total_users_job = 0

    #logic para excluir al cargo admin
    for job in jobs:
        if job.code != 'admin': 
            users_job = job.count_users_job()
            total_users_job += int(users_job)

    return render_template('admin/view_jobs.html',
                           title = title,
                           jobs = jobs,
                           prev_url = prev_url,
                           total_users_job = total_users_job)


@admin_bp.route('/jobs/<int:job_id>')
def view_job(job_id):
    title = 'Cargo'
    prev_url = url_for('admin.view_jobs')
    job= AdminServices.get_job(job_id)

    return render_template('admin/view_job.html',
                           title = title,
                           job = job,
                           prev_url = prev_url)


@admin_bp.route('/jobs/<int:job_id>/edit')
def edit_job(job_id):
    title = 'Editar cargo'
    prev_url = url_for('admin.view_job', job_id=job_id)
    job= AdminServices.get_job(job_id)
    job_form = None

    if job_form.validate_on_submit():
        code = job_form.code.data
        name = job_form.name.data
        description = job_form.description.data
        job = AdminServices.update_job(job_id, code, name, description)

    return render_template('admin/add_job.html',
                           title = title,
                           job = job,
                           prev_url = prev_url,
                           job_form = job_form)


@admin_bp.route('/jobs/add', methods=['GET', 'POST'])
@login_required
def add_job():
    title = 'Nuevo cargo'
    prev_url = url_for('admin.view_jobs')
    job_form = None
    if job_form.validate_on_submit():
        code = job_form.code.data
        name = job_form.name.data
        description = job_form.description.data

        try:
            new_job = AdminServices.create_job(code, name, description)
            current_app.logger.info(f'Cargo {new_job} CREATED!')
            flash("Cargo guardado exitosamente", 'success')
            return redirect(url_for('admin.view_jobs'))
        except Exception as e:
            current_app.logger.warning(f'Error al crear cargo: {e}')

    return render_template('admin/add_job.html',
                           title = title,
                           job_form = job_form,
                           prev_url = prev_url)