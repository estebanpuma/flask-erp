from flask_restful import Resource, marshal_with, abort, request, marshal

from ..core.resources import BaseGetResource, BasePatchResource, BaseDeleteResource, BasePostResource
from .services import PaymentPlanService, PaymentMethodService, InstallmentService, PaymentTransactionService
from .schemas import payment_method_fields, payment_plan_fields, installment_fields, transaction_fields

from ..core.utils import error_response, success_response, validation_error_response
from ..core.exceptions import AppError


class PaymentMethodCreateResource(BasePostResource):
    """
    Crea un nuevo método de pago.
    """
    service_create = staticmethod(PaymentMethodService.create_obj)
    output_fields = payment_method_fields


class PaymentMethodGetResource(BaseGetResource):
    '''
    Obtiene los metodos o metodo de pago
    '''
    schema_get = staticmethod(PaymentMethodService.get_obj)      #servicio para obtener un elemento
    schema_list = staticmethod(lambda: PaymentMethodService.get_obj_list(request.args.to_dict()))      #servicio para obtener una lista de elementos
    output_fields = payment_method_fields    #qué campos devolver(marshal)


class PaymentMethodUpdateResource(BasePatchResource):
    """
    PATCH /payment_methods/<id>
    Actualiza un método de pago existente.
    """
    service_get = staticmethod(PaymentMethodService.get_obj)
    service_patch = staticmethod(PaymentMethodService.patch_obj)
    output_fields = payment_method_fields


class PaymentMethodDeleteResource(BaseDeleteResource):
    """
    DELETE /payment_methods/<id>
    Elimina un método de pago por ID.
    """
    service_get = staticmethod(PaymentMethodService.get_obj)
    service_delete = staticmethod(PaymentMethodService.delete_obj)




#************************PaymentPlan*******************************
#**********************************************************

class PaymentPlanCreateResource(BasePostResource):
    """
    POST /payment_plans
    Crea un plan de pago vinculado a una orden.
    """
    service_create = staticmethod(PaymentPlanService.create_obj)
    output_fields = payment_plan_fields


class PaymentPlanGetResource(BaseGetResource):
    """
    GET
    Obtine el o los planes de pago vinculado a una orden
    """
    schema_get = staticmethod(PaymentPlanService.get_obj)      #servicio para obtener un elemento
    schema_list = staticmethod(lambda: PaymentPlanService.get_obj_list(request.args.to_dict()))      #servicio para obtener una lista de elementos
    output_fields = payment_plan_fields    #qué campos devolver(marshal)


class PaymentPlanPatchResource(BasePatchResource):
    service_get = staticmethod(PaymentPlanService.get_obj)
    service_patch = staticmethod(PaymentMethodService.patch_obj)
    output_fields = payment_plan_fields
        

class PaymentPlanDeleteResource(BaseDeleteResource):
    service_delete = staticmethod(PaymentPlanService.delete_obj)
    service_get = staticmethod(PaymentPlanService.get_obj)


#*****************************Installments************************************************

class PaymentTransactionPostResource(BasePostResource):
    service_create = staticmethod(PaymentTransactionService.create_obj)
    output_fields = transaction_fields

class PaymentTransactionGetResource(BaseGetResource):
    schema_get = staticmethod(PaymentTransactionService.get_obj)
    schema_list = staticmethod(lambda: PaymentTransactionService.get_obj_list(request.args.to_dict()))
    output_fields = transaction_fields

class InstallmentGetResource(Resource):
    @marshal_with(installment_fields)
    def get(self, id):
        return InstallmentService.get_obj(id)