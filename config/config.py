import os
from datetime import timedelta


class Config:
    DEBUG = True

    SECRET_KEY = 'THIS_SECRET_KEY_G0U8I0F4E5R0E0R9P12'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:password123@db:5432/erpdb')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'media')
    UPLOAD_FOLDERS = {
        'products': os.path.join(BASE_UPLOAD_FOLDER, 'products'),
        'clients': os.path.join(BASE_UPLOAD_FOLDER, 'clients'),
        'users': os.path.join(BASE_UPLOAD_FOLDER, 'users')
    }

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


    JWT_SECRET_KEY = 'super-clave-muy-segura-que-debes-cambiar'
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


   
