import os
from flask import current_app
from sqlalchemy.orm import joinedload
from app import db
from .models import Worker, Job
from ..core.exceptions import AppError, NotFoundError, ConflictError, ValidationError
from ..core.filters import apply_filters
from .dto_workers import WorkerCreateDTO, WorkerUpdateDTO
from .dto_jobs import JobCreateDTO, JobUpdateDTO
class AdminServices:
    
    @staticmethod
    def get_user(user_id):
        from .models import User
        return User.query.get_or_404(user_id)
    
    @staticmethod
    def get_all_users():
        from .models import User
        return User.query.all()
    
    @staticmethod
    def get_users_number():
        from .models import User
        total_users = User.query.all().count()
        return total_users-1
    
    
    @staticmethod
    def get_job(job_id):
        from .models import Job
        return Job.query.get_or_404(job_id)

    @staticmethod
    def get_all_jobs():
        from .models import Job
        return Job.query.all()
    
    
    @staticmethod
    def get_role(role_id):
        from .models import Role
        return Role.query.get_or_404(role_id)

    @staticmethod
    def get_all_roles():
        from .models import Role
        return Role.query.all()
    
    @staticmethod
    def get_users_with_role_ids(role_id):
        from .models import Role, User, user_roles

        # Consulta para obtener usuarios que tengan alguno de los roles especificados
        users_with_role = User.query.join(Role).filter(Role.id==role_id).all()
       
        return users_with_role

    @staticmethod
    def get_users_with_role_codes(role_codes:list):
        from .models import Role, User, user_roles

        # Consulta para obtener usuarios que tengan alguno de los roles especificados
        users_with_role = User.query.join(Role).filter(Role.code.in_(role_codes)).all()
       
        return users_with_role
    
    @staticmethod
    def get_users_by_type(type:str):
        from .models import Role, User

        # Consulta para obtener usuarios por tipo
        users= User.query.filter(User.user_type == type).all()
       
        return users


    

    @staticmethod
    def create_user(username, ci, email, password, job_code=None, phone=None):
        from .models import User, Job, Salesperson, SalesSupervisor, ProductionManager, ProductionOperator, WarehouseKeeper

        existing_user = User.query.filter_by(ci=ci).first()
        if existing_user:
            raise ValueError("A user with this CI already exists")

        job_classes = {
            'VEN-GEN': Salesperson,
            'VEN-SUP': SalesSupervisor,
            'PRO-OPE': ProductionOperator,
            'PRO-JEF': ProductionManager,
            'INV-BOD': WarehouseKeeper,
        }

        # Obtiene la clase del usuario basado en job_code, o usa User si no se encuentra
        user_class = job_classes.get(job_code, User)

        # Crea la instancia de usuario
        user = user_class(
            username=username,
            ci=ci,
            email=email,
            phone=phone,
            job_code=job_code
        )
        user.set_password(password)
        job = Job.query.filter(Job.code==job_code).first()
        role = AdminServices.create_role(code=job.code,
                                         name=job.name,
                                         description=job.description)
        user.roles = [role]
        try:
            

            # Añadir el vendedor a la sesión y guardar
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f'Admin user {user.username} created successfully')
            return user
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error creating user: {str(e)}')
        

    def update_job(job_id, code, name, description=None):
        job = AdminServices.get_job(job_id)
        
        job.code = code
        job.name = name
        job.descripiton = description

        try:
            db.session.add(job)
            db.session.commit()
            current_app.logger.info(f'Job {job.name} UPDATED successfully')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error UPDATING JOB: {str(e)}')

    @staticmethod
    def initialize_admin_user():
        """Inicializa el usuario admin si no existe. Crea roles y trabajos necesarios."""
        from .models import User

        # Verificar si ya existe un usuario admin
        admin = User.query.filter_by(username='Administrator').first()
        if admin:
            current_app.logger.info('Admin user already exists')
            return

        # Obtener datos del admin desde variables de entorno
        username = os.environ.get('ADMIN_USER_NAME')
        email = os.environ.get('ADMIN_USER_EMAIL')
        password = os.environ.get('ADMIN_USER_PASSWORD')
        ci = '0000000000'
        print([username, email, password])

        if not all([username, email, password]):
            raise ValueError("Admin credentials not fully set in environment variables")

        # Crear el usuario admin
        admin_user = User(ci=ci, username=username, email=email)
        admin_user.set_password(password)

        # Crear roles y permisos básicos si no existen
        
        admin_job = AdminServices.create_job('admin', 'Administrator', 'Administrator')
        admin_role = AdminServices.create_role('admin', 'Administrator', 'Administrator')
       

        # Asignar rol de admin y trabajo al usuario
        admin_user.job_code = admin_job.code
        admin_user.roles = [admin_role]

        try:
            db.session.add(admin_user)
            db.session.commit()
            current_app.logger.info(f'Admin user {admin_user.username} created successfully')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error creating admin user: {str(e)}')


    @staticmethod
    def create_job(code, name, description=None):
        """Crea un trabajo si no existe."""
        from .models import Job
        job = Job.query.filter_by(code=code).first()
        if not job:
            job = Job(code=code, name=name, description=description)
            try:
                db.session.add(job)
                db.session.commit()
                current_app.logger.info(f'Job {name} created successfully')
            except Exception as e:
                db.session.rollback()
                current_app.logger.warning(f'Error creating job {name}: {str(e)}')
            
            AdminServices.create_role(code=code, name=name, description=description)

        else:
            current_app.logger.warning(f'Registro con el codigo {code} ya existe')
            #raise KeyError(f'Registro con el codigo {code} ya existe')
        
        return job
    
    @staticmethod
    def create_role(code, name, description=None):
        """Crea un rol si no existe."""
        from .models import Role
        role = Role.query.filter_by(code=code).first()
        if not role:
            role = Role(code=code, name=name, description=description)
            try:
                db.session.add(role)
                db.session.commit()
                current_app.logger.info(f'Role {name} created successfully')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f'Error creating role {name}: {str(e)}')
        
        else:
            current_app.logger.warning(f'Registro con el codigo {code} ya existe')
            #raise ValueError(f'Registro con el codigo {code} ya existe')
        
        return role
    
    @staticmethod
    def update_roles(user_id, roles):

        user = AdminServices.get_user(user_id)

        user.roles = []

        from .models import Role
        new_roles = []

        for role in roles:
            new_role = Role.query.filter_by(code=role).first()
            if new_role:
                new_roles.append(new_role)

        user.roles = [new_role for new_role in new_roles]

        try:
            db.session.commit()
            current_app.logger.info(f'Role updated successfully')
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error updatibg roles: {str(e)}')
        
        return new_roles
    

class WorkerService:

    @staticmethod
    def get_obj(id):
        worker = db.session.query(Worker).get(id)
        if not worker:
            raise NotFoundError(f'No existe un trabajador con ID:{id}')
        return worker
    
    @staticmethod
    def get_obj_list(filters:dict=None):
        query = apply_filters(Worker, filters, query_only=True)
        workers = query.options(joinedload(Worker.job)).all()    
        return workers
    
    @staticmethod
    def search_workers(q:str, limit=10):
        q = q.strip().lower()
        query =( db.session.query(Worker)
                .filter(
                        (Worker.ci.ilike(f'%{q}%')) |
                        (Worker.first_name.ilike(f'%{q}%')) |
                        (Worker.last_name.ilike(f'%{q}%'))
                )
                .order_by(Worker.first_name.asc())
                .limit(limit)
                .all()
        )

        return query
    
    @staticmethod
    def create_obj(data:dict)->Worker:
        with db.session.begin():
            dto = WorkerCreateDTO(**data)
            worker = WorkerService.create_worker(first_name=dto.first_name,
                                                 last_name=dto.last_name,
                                                 ci=dto.ci,
                                                 job_id=dto.job_id,
                                                 worker_type=dto.worker_type,
                                                 hour_rate_normal=dto.hour_rate_normal,
                                                 salary=dto.salary,
                                                 phone=dto.phone,
                                                 notes=dto.notes
                                                 )
            return worker
    
    @staticmethod
    def create_worker(first_name:str,
                      last_name:str,
                      ci:str,
                      worker_type:str,
                      hour_rate_normal:float=None,
                      salary:float=None,
                      job_id:int=None,
                      phone:str= None,
                      notes:str=None
                      ):
        
        if job_id is not None:
            job = Job.query.get(job_id)
            if not job:
                raise ValidationError(f'No existe un puesto de trabajo con ID: {job_id}')
        if salary is None and hour_rate_normal is None:
            raise ValidationError('Debe ingresar el salrio o el pago por horas')
        
        worker = Worker(first_name=first_name,
                        last_name = last_name,
                        ci = ci,
                        phone = phone,
                        job_id = job_id,
                        worker_type = worker_type,
                        hour_rate_normal = hour_rate_normal,
                        salary = salary,
                        notes = notes
                        )
        if salary is not None:
            worker.calculate_hour_rate()
        

        db.session.add(worker)
        return worker
    

        
    @staticmethod
    def patch_obj(worker: Worker, data: dict) -> Worker:
    
        dto = WorkerUpdateDTO(**data)
        return WorkerService.update_worker(worker, dto)


    @staticmethod
    def update_worker(worker: Worker, dto) -> Worker:
        if dto.first_name is not None:
            worker.first_name = dto.first_name.strip()

        if dto.last_name is not None:
            worker.last_name = dto.last_name.strip()

        if dto.phone is not None:
            worker.phone = dto.phone.strip()

        if dto.notes is not None:
            worker.notes = dto.notes.strip()

        if dto.worker_type is not None:
            worker.worker_type = dto.worker_type

        if dto.salary is not None:
            worker.salary = dto.salary
            # Recalcular tarifa horaria si se cambia el salario
            worker.calculate_hour_rate()

        if dto.hour_rate_normal is not None:
            worker.hour_rate_normal = dto.hour_rate_normal

        if dto.is_active is not None:
            worker.is_active = dto.is_active

        if dto.job_id is not None:
            job = Job.query.get(dto.job_id)
            if not job:
                raise ValidationError(f'No existe un puesto de trabajo con ID: {dto.job_id}')
            worker.job_id = dto.job_id

        db.session.commit()
        return worker

            
class JobService:

    @staticmethod
    def get_obj(id):
        job = db.session.query(Job).options(joinedload(Job.workers)).get(id)
        if not job:
            raise NotFoundError(f'No existe un puesto de trabajo con ID:{id}')
        return job
    
    @staticmethod
    def get_obj_list(filters=None)->list[Job]:
        return apply_filters(Job, filters)
    
    @staticmethod
    def create_obj(data:dict)->Job:
        with db.session.begin():
            dto = JobCreateDTO(**data)
            job = JobService.create_job(dto.code, dto.name, dto.description)
            return job

    @staticmethod
    def create_job(code:str, name:str, description:str=None)->Job:
        job = Job.query.filter(Job.code==code).first()
        if job:
            raise ValidationError(f'Ya existe un puesto de trabajo con el codigo:{code}. Puesto:{job.name}')
        job = Job.query.filter(Job.name==name).first()
        if job:
            raise ValidationError(f'Ya existe un puesto de trabajo con el nombre:{job.name}')
        
        new_job = Job(code=code,
                      name=name,
                      description=description
                        )
        
        db.session.add(new_job)
        return new_job
    
    @staticmethod
    def patch_obj(obj:Job, data:dict)->Job:
        print('entra a patch obj')
        dto = JobUpdateDTO(**data)
        job = JobService.patch_job(obj, dto.name, dto.description)
        return job

    @staticmethod
    def patch_job(obj:Job, name:str=None, description:str=None):
        print('entra a job')
        if name:
            if obj.name != name:
                obj.name = name
        if description:
            obj.description = description

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.warning(f'error: {e}')
            db.session.rollback()
            raise str(e)
        
    @staticmethod
    def search_job(q:str, limit=10)->list[Job]:
        query = (db.session.query(Job)
                 .filter(
                     (Job.code.ilike(f'%{q}%')) |
                     (Job.description.ilike(f'%{q}%'))
                 )
                 .limit(limit)
                 .order_by(Job.name.asc())
                 .all()
                )

        return query
