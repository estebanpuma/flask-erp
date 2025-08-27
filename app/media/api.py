from flask_restful import Api
from flask import Blueprint
from .resources import ImageResource, ImageListGetReource

media_api_bp = Blueprint('media', __name__, url_prefix='/api/v1/media')


api = Api(media_api_bp)


api.add_resource(ImageListGetReource, '/<module>/<int:model_id>')

api.add_resource(ImageResource, '/img/<module>/<filename>')




