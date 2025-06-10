from flask_restful import Resource, abort, marshal, marshal_with, request
from sqlalchemy.exc import SQLAlchemyError

from flask import jsonify, make_response, current_app

from .services import AdminServices, WorkerService, JobService
from .schemas import user_fields, job_fields, role_fields, worker_fields, job_workers_fields

from ..core.utils import success_response, error_response, validation_error_response

from ..core.resources import BaseDeleteResource, BaseGetResource, BasePatchResource, BasePostResource, BasePutResource



class UserGetResource(BaseGetResource):
    schema_get = staticmethod(AdminServices.get_user)       #servicio para obtener un elemento
    schema_list = staticmethod(AdminServices.get_all_users)      #servicio para obtener una lista de elementos
    output_fields = user_fields    #qué campos devolver(marshal)


class UserPostResource(BasePostResource):
    pass


class UserPatchResource(BasePatchResource):
    pass


class UserDeleteResource(BaseDeleteResource):
    pass


class UserResource(Resource):

    @marshal_with(user_fields)
    def get(self, user_id=None):
        
        
        try:
            q=request.args.get('role')
            print(q)
            if q:
                users = AdminServices.get_users_by_type(q)
                print(q, users)
                return users, 200 if users else abort(404)


            users = AdminServices.get_users_with_role_codes
            if user_id:
                user = AdminServices.get_user(user_id)
                if not user:
                    abort(404, message='Usuario no encontrado')
        
                return user, 200
            
            users = AdminServices.get_all_users()
            return users, 200
        
        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching users(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message="Unexpected error occurred")

    
    def put(self, user_id):
        pass

        
class JobResource(Resource):

    @marshal_with(job_fields)
    def get(self, job_id=None):
        try:
            if job_id:
                job = AdminServices.get_job(job_id)
                if not job:
                    abort(404, message="Job not found")
                    
                return job, 200

            jobs = AdminServices.get_all_jobs()
            
            return jobs, 200

        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching job(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message="Unexpected error occurred")


    def post():

        pass

    def put():
        pass

    def delete():
        pass



class RoleResource(Resource):

    @marshal_with(role_fields)
    def get(self, role_id=None):
        try:
            if role_id:
                role = AdminServices.get_role(role_id)
                if not role:
                    abort(404, 'No encontrado')
                
                return role, 200
            
            roles = AdminServices.get_all_roles()
            return roles, 200

        except SQLAlchemyError as e:
            current_app.logger.error(f'Error fetching job(s): {e}')
            abort(500, message="Internal server error")
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {e}')
            abort(500, message="Unexpected error occurred")








class WorkerGetResource(BaseGetResource):
    schema_get = staticmethod(WorkerService.get_obj)       #servicio para obtener un elemento
    schema_list = staticmethod(WorkerService.get_obj_list)      #servicio para obtener una lista de elementos
    output_fields = worker_fields    #qué campos devolver(marshal)

class WorkerPostResource(BasePostResource):
    service_create = staticmethod(WorkerService.create_obj)   
    output_fields = worker_fields

class WorkerSearchResource(Resource):
    def get(self):
        q = request.args.to_dict()
        if 'q' in q:
            workers = WorkerService.search_workers(str(q['q']))
            return success_response(marshal(workers, worker_fields), 200)
        


#-----------------------------Jobs-------------------------------------------------

class JobGetResource(BaseGetResource):
    schema_get = staticmethod(JobService.get_obj)       #servicio para obtener un elemento
    schema_list = staticmethod(lambda: JobService.get_obj_list(request.args.to_dict()))      #servicio para obtener una lista de elementos
    output_fields = job_workers_fields   #qué campos devolver(marshal)

class JobPostResource(BasePostResource):
    service_create = staticmethod(JobService.create_obj)   
    output_fields = job_fields

class JobPatchResource(BasePatchResource):
    service_get = staticmethod(JobService.get_obj)       #servicio para obtener un elemento
    service_patch = staticmethod(JobService.patch_obj)
    output_fields = job_fields    #qué campos devolver(marshal)

class JobSearchResource(Resource):
    def get(self):
        q = request.args.to_dict()
        if 'q' in q:
            jobs = JobService.search_job(str(q['q']))
            return success_response(marshal(jobs, job_fields), 200)