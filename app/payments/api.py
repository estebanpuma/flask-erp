from flask_restful import Api
from flask import Blueprint
from .resources import PaymentMethodCreateResource, PaymentMethodGetResource, PaymentMethodUpdateResource, PaymentMethodDeleteResource
from .resources import PaymentPlanCreateResource, PaymentPlanGetResource

payments_api_bp = Blueprint('payments_api_bp', __name__, url_prefix='/api/v1')
payments_api = Api(payments_api_bp)


payments_api.add_resource(PaymentMethodGetResource, '/payment_methods', '/payment_methods/<int:resource_id>')

payments_api.add_resource(PaymentMethodCreateResource, '/payment_methods')

payments_api.add_resource(PaymentMethodUpdateResource,'/payment_methods/<int:resource_id>')

payments_api.add_resource(PaymentMethodDeleteResource, '/payment_methods/<int:resource_id>')


payments_api.add_resource(PaymentPlanCreateResource, '/payment_plans')

payments_api.add_resource(PaymentPlanGetResource, '/payment_plans', '/payment_plans/<int:resource_id>')
