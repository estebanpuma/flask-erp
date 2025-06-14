from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from app import db

from app.common.models import BaseModel, SoftDeleteMixin


class User(UserMixin, BaseModel):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    ci = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(150))
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    phone = db.Column(db.String(20), nullable=True)
    job_code = db.Column(db.String(), db.ForeignKey('jobs.code'))
    user_type = db.Column(db.String())

    job = db.relationship('Job', back_populates='users')
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')


    __mapper_args__ = {
        'polymorphic_identity': 'employee',  # Identidad para la clase base
        'polymorphic_on': user_type  # Campo que se usará para distinguir subclases
    }

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)


class Salesperson(User):

    __tablename__ = 'salespersons'

    __mapper_args__ = {'polymorphic_identity': 'salesperson'}

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    sales_orders_count = db.Column(db.Integer, default=0)
    visits = db.Column(db.Integer, default=0)
    
    sale_orders = db.relationship('SaleOrder', back_populates='salesperson')


class SalesSupervisor(User):

    __tablename__ = 'sales_supervisors'

    __mapper_args__ = {'polymorphic_identity': 'sales_supervisor'}

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    sales_orders_count = db.Column(db.Integer, default=0)
    visits = db.Column(db.Integer, default=0)
    
    


class WarehouseKeeper(User):

    __tablename__ = 'warehouse_keepers'

    __mapper_args__ = {'polymorphic_identity': 'warehouse_keeper'}

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)


class ProductionManager(User):

    __tablename__ = 'production_managers'

    __mapper_args__ = {'polymorphic_identity': 'production_manager'}

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)


class ProductionOperator(User):

    __tablename__ = 'production_operators'

    __mapper_args__ = {'polymorphic_identity': 'production_operator'}

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)    


# Tabla de asociación entre usuarios y roles
user_roles = db.Table('user_roles',
    db.Column('user_ci', db.String(), db.ForeignKey('users.ci', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
    db.Column('role_code', db.String(), db.ForeignKey('roles.code', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
)


class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(), unique=True, nullable=False)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200), nullable=True)

    users = db.relationship('User', secondary='user_roles', back_populates='roles')

    


class Job(db.Model, SoftDeleteMixin):

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120))
    description = db.Column(db.String(200), nullable=True)

    users = db.relationship('User', back_populates='job')

    workers = db.relationship('Worker', back_populates='job')

    @property
    def count_users_job(self):
        user_job = User.query.join(Job).filter(Job.code == self.code,
                                               User.is_active == True).all()
        return len(user_job)
    
    @property
    def count_workers_job(self):
        worker_job = Worker.query.join(Job).filter(Job.code == self.code,
                                               Worker.is_active == True).all()
        return len(worker_job)


    


class Worker(BaseModel, SoftDeleteMixin):

    __tablename__ = 'workers'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    ci = db.Column(db.String(10), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    worker_type = db.Column(db.String(), nullable=False)#planta/rotativo/contratista
    salary = db.Column(db.Float(), nullable=True)
    phone = db.Column(db.String(), nullable=True)
    hour_rate_normal = db.Column(db.Float)
    notes = db.Column(db.String(), nullable=False)

    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True )
    
    job = db.relationship('Job', back_populates='workers')

    @property
    def calculate_hour_rate(self):
        calculated_hour_rate = self.salary / 173.2 #40 horas/semana × 4.33 semanas/mes = 173.2 horas/mes (4.33 es el promedio de semanas por mes: 52 semanas/año ÷ 12 meses)
        self.hour_rate_normal = calculated_hour_rate
        return calculated_hour_rate
    
    @property
    def hour_rate_overtime(self, worked_week_hours:float):
        if worked_week_hours <= 45 and worked_week_hours > 40:
            return self.hour_rate_normal*1.25
        
        if worked_week_hours <= 50 and worked_week_hours > 45:
            return self.hour_rate_normal*1.5
        
        if worked_week_hours > 50:
            return self.hour_rate_normal*2