from flask_restful import Resource, marshal_with, abort, request

from ..core.resources import BaseGetResource, BasePutResource, BasePatchResource, BaseDeleteResource, BasePostResource
from .services import PaymentServices
from .schemas import payment_method_fields, payment_plan_fields
from .validations import validate_payment_method_data, validate_payment_method_patch_data
from .validations import validate_payment_plan_data


class PaymentMethodCreateResource(BasePostResource):
    """
    Crea un nuevo método de pago.
    """
    schema = staticmethod(validate_payment_method_data)
    service_create = staticmethod(PaymentServices.create_obj)
    output_fields = payment_method_fields


class PaymentMethodGetResource(BaseGetResource):
    '''
    Obtiene los metodos o metodo de pago
    '''
    schema_get = staticmethod(PaymentServices.get_obj)      #servicio para obtener un elemento
    schema_list = staticmethod(lambda: PaymentServices.get_obj_list(request.args.to_dict()))      #servicio para obtener una lista de elementos
    output_fields = payment_method_fields    #qué campos devolver(marshal)


class PaymentMethodUpdateResource(BasePatchResource):
    """
    PATCH /payment_methods/<id>
    Actualiza un método de pago existente.
    """
    schema_validate_partial = staticmethod(validate_payment_method_patch_data)
    service_get = staticmethod(PaymentServices.get_obj)
    service_patch = staticmethod(PaymentServices.patch_obj)
    output_fields = payment_method_fields


class PaymentMethodDeleteResource(BaseDeleteResource):
    """
    DELETE /payment_methods/<id>
    Elimina un método de pago por ID.
    """
    service_delete = staticmethod(PaymentServices.delete_obj)



class PaymentPlanCreateResource(BasePostResource):
    """
    POST /payment_plans
    Crea un plan de pago vinculado a una orden.
    """
    schema = staticmethod(validate_payment_plan_data)
    service_create = staticmethod(PaymentServices.create_payment_plan)
    output_fields = payment_plan_fields


class PaymentPlanGetResource(BaseGetResource):
    """
    GET
    Obtine el o los planes de pago vinculado a una orden
    """
    schema_get = staticmethod(PaymentServices.get_payment_plan)      #servicio para obtener un elemento
    schema_list = staticmethod(PaymentServices.get_payment_plans)      #servicio para obtener una lista de elementos
    output_fields = payment_plan_fields    #qué campos devolver(marshal)