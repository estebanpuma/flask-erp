from flask import Blueprint, render_template


workers_bp = Blueprint('workers', __name__, url_prefix='/workers', template_folder='../templates')


@workers_bp.route('/')
def workers_list():
    return render_template('workers/workers_list.html')

@workers_bp.route('/<int:id>')
def workers_details(id):
    return render_template('workers/workers_detail.html', worker_id=id)

@workers_bp.route('/create')
def workers_create():
    return render_template('workers/workers_create.html')

@workers_bp.route('/<int:id>/edit')
def workers_edit(id):
    from ...admin.services import WorkerService, AdminServices
    worker = WorkerService.get_obj(id)
    jobs = AdminServices.get_all_jobs()
    return render_template('workers/workers_edit.html', worker_id=id, worker= worker, jobs=jobs)



#******************Jobs****************************



@workers_bp.route('/jobs')
def jobs_list():
    return render_template('jobs/job_list.html')

@workers_bp.route('/jobs/<int:id>')
def jobs_details(id):
    return render_template('jobs/job_detail.html', job_id=id)

@workers_bp.route('/jobs/create')
def jobs_create():
    return render_template('jobs/job_create.html')

@workers_bp.route('/jobs/<int:id>/edit')
def jobs_edit(id):
    return render_template('jobs/job_edit.html', job_id=id)