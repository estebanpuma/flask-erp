import os
from datetime import timedelta

from pathlib import Path


class Config:
    DEBUG = True

    SECRET_KEY = 'THIS_SECRET_KEY_G0U8I0F4E5R0E0R9P12'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:password123@db:5432/erpdb')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    # __file__ → /path/to/project/app/config.py
    CONFIG_PATH = Path(__file__).resolve()

    # dos niveles arriba, si fuese necesario:
    PROJECT_ROOT = CONFIG_PATH.parents[1]

    BASEDIR = str(os.path.join(PROJECT_ROOT, 'app'))

    
    BASE_UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'media')

    UPLOAD_FOLDERS = {
        'products': os.path.join(BASE_UPLOAD_FOLDER, 'products'),
        'designs':  os.path.join(BASE_UPLOAD_FOLDER, 'designs'),
        'clients': os.path.join(BASE_UPLOAD_FOLDER, 'clients'),
        'users': os.path.join(BASE_UPLOAD_FOLDER, 'users')
    }

    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


    JWT_SECRET_KEY = 'super-clave-muy-segura-que-debes-cambiar'
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


   
