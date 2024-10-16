from flask_restful import Resource, abort, marshal, marshal_with
from sqlalchemy.exc import SQLAlchemyError

from flask import jsonify, make_response, current_app

from .services import AdminServices
from .schemas import user_fields, job_fields, role_fields


class UserResource(Resource):

    @marshal_with(user_fields)
    def get(self, user_id=None):
        try:
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