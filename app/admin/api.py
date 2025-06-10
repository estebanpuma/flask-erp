from flask import Blueprint
from flask_restful import Api
from .resources import (
    WorkerGetResource,
    WorkerPostResource,
    WorkerSearchResource,

    JobGetResource,
    JobPatchResource,
    JobPostResource,
    JobSearchResource


)


admin_api_bp = Blueprint('admin', __name__, url_prefix='/api/v1')
admin_api = Api(admin_api_bp)


admin_api.add_resource(WorkerGetResource, '/workers', '/workers/<int:resource_id>')
admin_api.add_resource(WorkerPostResource, '/workers')
admin_api.add_resource(WorkerSearchResource, '/workers/search')

admin_api.add_resource(JobGetResource, '/jobs', '/jobs/<int:resource_id>')
admin_api.add_resource(JobPostResource, '/jobs')
admin_api.add_resource(JobPatchResource, '/jobs/<int:resource_id>')
admin_api.add_resource(JobSearchResource, '/jobs/search')