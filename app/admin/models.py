from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from app import db

from app.common.models import BaseModel


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

    


class Job(db.Model):

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120))
    description = db.Column(db.String(200), nullable=True)

    users = db.relationship('User', back_populates='job')

    def count_users_job(self):
        user_job = User.query.join(Job).filter(Job.code == self.code).all()
        return len(user_job)


    