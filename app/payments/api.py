from flask_restful import Api
from flask import Blueprint
from .resources import (PaymentMethodCreateResource, 
                        PaymentMethodGetResource, 
                        PaymentMethodUpdateResource, 
                        PaymentMethodDeleteResource,

                        PaymentTransactionCreateResource,
                        PaymentTransactionDeleteResource,
                        PaymentTransactionGetResource,
                        PaymentTransactionUpdateResource,
                        SalesPaymentTransactionGetResource,

                        PaymentAgreementCreateResource,
                        PaymentAgreementDeleteResource,
                        PaymentAgreementGetResource,
                        PaymentAgreementUpdateResource,
                        SalesPaymentAgreementGetResource
                        )


payments_api_v1_bp = Blueprint('payments_api_bp', __name__, url_prefix='/api/v1')
payments_api = Api(payments_api_v1_bp)


payments_api.add_resource(PaymentMethodGetResource, '/payment-methods', '/payment-methods/<int:resource_id>')
payments_api.add_resource(PaymentMethodCreateResource, '/payment-methods')
payments_api.add_resource(PaymentMethodUpdateResource,'/payment-methods/<int:resource_id>')
payments_api.add_resource(PaymentMethodDeleteResource, '/payment-methods/<int:resource_id>')


payments_api.add_resource(PaymentTransactionGetResource, '/payment-transactions', '/payment-transactions/<int:resource_id>')
payments_api.add_resource(SalesPaymentTransactionGetResource, '/payment-transactions/<int:resource_id>/sale-order')
payments_api.add_resource(PaymentTransactionCreateResource, '/payment-transactions')
payments_api.add_resource(PaymentTransactionUpdateResource,'/payment-transactions/<int:resource_id>')
payments_api.add_resource(PaymentTransactionDeleteResource, '/payment-transactions/<int:resource_id>')


#*********************Agreements***********************************
payments_api.add_resource(PaymentAgreementGetResource, '/payment-agreements', '/payment-agreements/<int:resource_id>')
payments_api.add_resource(SalesPaymentAgreementGetResource, '/payment-agreements/<int:resource_id>/sale-order')
payments_api.add_resource(PaymentAgreementCreateResource, '/payment-agreements')
payments_api.add_resource(PaymentAgreementUpdateResource,'/payment-agreements/<int:resource_id>')
payments_api.add_resource(PaymentAgreementDeleteResource, '/payment-agreements/<int:resource_id>')