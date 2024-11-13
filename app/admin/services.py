import os
from flask import current_app
from app import db

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
    def get_users_with_role(role_id):
        from .models import Role, User, user_roles

        # Consulta para obtener usuarios que tengan alguno de los roles especificados
        users_with_role = User.query.join(Role).filter(Role.id==role_id).all()
       
        return users_with_role

    

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