from flask import Blueprint
from flask_restful import Api

from .resources import MediaDeleteResource, MediaServeResource, MediaUploadResource

media_api_bp = Blueprint("media", __name__, url_prefix="/api/v1/media")


api = Api(media_api_bp)

# Endpoint genérico para subir archivos
api.add_resource(MediaUploadResource, "/upload/<module>")

# Endpoint para servir los archivos de forma segura
api.add_resource(MediaServeResource, "/img/<module>/<filename>")

api.add_resource(MediaDeleteResource, "/delete/<module>/<image_id>")
