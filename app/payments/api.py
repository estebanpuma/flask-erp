from flask_restful import Api
from .resources import PaymentMethodResource
from . import payments_bp

payments_api = Api(payments_bp)


payments_api.add_resource(PaymentMethodResource, '/api/v1/payment_methods', '/api/v1/payment_methods/<int:id>')