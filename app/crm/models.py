import enum

from sqlalchemy import Enum

from app import db

from ..common import BaseModel, SoftDeleteMixin



class ClientCategory(BaseModel, SoftDeleteMixin):  # Usando eliminación suave

    __tablename__ = 'client_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True) 

    def __repr__(self):
        return f'<Categoria_cliente(nombre={self.name})>'


class Client(BaseModel):

    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    #info general
    name = db.Column(db.String(200), nullable=False)
    ruc_or_ci = db.Column(db.String(13), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=True, unique=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    #ubicacion
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), nullable=False)
    canton_id = db.Column(db.Integer, db.ForeignKey('cantons.id'), nullable=False)
    #clasificacion
    client_type = db.Column(db.String(20), nullable=False)
    client_category_id = db.Column(db.Integer, db.ForeignKey('client_categories.id', ondelete='RESTRICT'), nullable=True)
    
    
    is_special_taxpayer = db.Column(db.Boolean, default=False)
    

    client_category = db.relationship('ClientCategory', backref='clients')
    contacts = db.relationship('Contact', back_populates='client', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('SaleOrder', back_populates='client', cascade="all, delete-orphan")
    province = db.relationship('Provinces', back_populates='clients')
    canton = db.relationship('Cantons', back_populates='clients')
    
    def __repr__(self):
        return f'<Cliente(nombre={self.name}, ruc_o_cedula={self.ruc_or_ci})>'


class Contact(BaseModel):

    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)  
    birth_date = db.Column(db.Date, nullable=True)  
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    client = db.relationship('Client', back_populates='contacts')
    
    def __repr__(self):
        return f'<Contacto(nombre={self.name}, client={self.client.name})>'


class Provinces(db.Model):

    __tablename__ = 'provinces'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(6), nullable=False, unique=True)
    capital = db.Column(db.String(100), nullable=True)
    population = db.Column(db.Integer, nullable=True)
    cantons = db.relationship('Cantons', back_populates='province', cascade='all, delete-orphan')
    clients = db.relationship('Client', back_populates='province')
    
    def __repr__(self):
        return f'<Provincia(nombre={self.name})>'
    

class Cantons(db.Model):

    __tablename__ = 'cantons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(6), nullable=True, unique=False)
    population = db.Column(db.Integer, nullable=True)
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), nullable=False)
    province = db.relationship('Provinces', back_populates='cantons')
    clients = db.relationship('Client', back_populates='canton')
    
    
    def __repr__(self):
        return f'<Cantón(nombre={self.name})>'