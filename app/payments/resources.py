from flask_restful import Resource, marshal_with, abort, request

from .services import PaymentMethodService
from .schemas import payment_method_fields

class PaymentMethodResource(Resource):

    @marshal_with(payment_method_fields)
    def get(self, id=None):
        try:
            if id:
                method = PaymentMethodService.get_payment_method(id)
                return method, 200 if method else abort(400)
            methods = PaymentMethodService.get_all_payment_methods()
            return methods, 200 if methods else abort(400)
        except Exception as e:
            abort(500, message=f'{str(e)}')