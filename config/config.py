import os

class Config:
    DEBUG = True

    SECRET_KEY = 'THIS_SECRET_KEY_G0U8I0F4E5R0E0R9P12'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:password123@db:5432/erpdb')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
