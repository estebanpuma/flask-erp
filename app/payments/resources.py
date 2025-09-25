from flask_restful import request

from ..core.resources import (
    BaseDeleteResource,
    BaseGetResource,
    BasePatchResource,
    BasePostResource,
)
from .schemas import agreement_fields, payment_method_fields, transaction_fields
from .services import (
    PaymentAgreementService,
    PaymentMethodService,
    PaymentTransactionService,
)


class PaymentMethodCreateResource(BasePostResource):
    """
    Crea un nuevo método de pago.
    """

    service_create = staticmethod(PaymentMethodService.create_obj)
    output_fields = payment_method_fields


class PaymentMethodGetResource(BaseGetResource):
    """
    Obtiene los metodos o metodo de pago
    """

    schema_get = staticmethod(
        PaymentMethodService.get_obj
    )  # servicio para obtener un elemento
    schema_list = staticmethod(
        lambda: PaymentMethodService.get_obj_list(request.args.to_dict())
    )  # servicio para obtener una lista de elementos
    output_fields = payment_method_fields  # qué campos devolver(marshal)


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


# /*************************Transactions*************************
class PaymentTransactionCreateResource(BasePostResource):
    """
    Crea un nuevo pago.
    """

    service_create = staticmethod(PaymentTransactionService.create_obj)
    output_fields = transaction_fields


class PaymentTransactionGetResource(BaseGetResource):
    """
    Obtiene los los pagos
    """

    schema_get = staticmethod(
        PaymentTransactionService.get_obj
    )  # servicio para obtener un elemento
    schema_list = staticmethod(
        lambda: PaymentTransactionService.get_obj_list(request.args.to_dict())
    )  # servicio para obtener una lista de elementos
    output_fields = transaction_fields  # qué campos devolver(marshal)


class SalesPaymentTransactionGetResource(BaseGetResource):
    """Pagos por orden de venta"""

    schema_get = staticmethod(PaymentTransactionService.get_sale_payments)
    output_fields = transaction_fields


class PaymentTransactionUpdateResource(BasePatchResource):
    """
    PATCH /payment_methods/<id>
    Actualiza un pago existente.
    """

    service_get = staticmethod(PaymentTransactionService.get_obj)
    service_patch = staticmethod(PaymentTransactionService.patch_obj)
    output_fields = transaction_fields


class PaymentTransactionDeleteResource(BaseDeleteResource):
    """
    DELETE /payment_methods/<id>
    Elimina un pago.
    """

    service_get = staticmethod(PaymentTransactionService.get_obj)
    service_delete = staticmethod(PaymentTransactionService.delete_obj)


# /*************************Agreements*************************
class PaymentAgreementCreateResource(BasePostResource):
    """
    Crea un nuevo pago.
    """

    service_create = staticmethod(PaymentAgreementService.create_obj)
    output_fields = agreement_fields


class PaymentAgreementGetResource(BaseGetResource):
    """
    Obtiene los los pagos
    """

    schema_get = staticmethod(
        PaymentAgreementService.get_obj
    )  # servicio para obtener un elemento
    schema_list = staticmethod(
        lambda: PaymentAgreementService.get_obj_list(request.args.to_dict())
    )  # servicio para obtener una lista de elementos
    output_fields = agreement_fields  # qué campos devolver(marshal)


class SalesPaymentAgreementGetResource(BaseGetResource):
    """Pagos por orden de venta"""

    schema_get = staticmethod(PaymentAgreementService.get_sale_agreements)
    output_fields = agreement_fields


class PaymentAgreementUpdateResource(BasePatchResource):
    """
    PATCH /payment_methods/<id>
    Actualiza un pago existente.
    """

    service_get = staticmethod(PaymentAgreementService.get_obj)
    service_patch = staticmethod(PaymentAgreementService.patch_obj)
    output_fields = agreement_fields


class PaymentAgreementDeleteResource(BaseDeleteResource):
    """
    DELETE /payment_methods/<id>
    Elimina un pago.
    """

    service_get = staticmethod(PaymentAgreementService.get_obj)
    service_delete = staticmethod(PaymentAgreementService.delete_obj)
