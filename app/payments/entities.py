from ..common.parsers import (
    parse_int, parse_float, parse_date, parse_str
)
from ..sales.services import SaleOrderService

from ..core.exceptions import ValidationError

from datetime import date


class PAymentMethodEntity():
    def __init__(self, data: dict):
        self.name = parse_str(data.get('name'), field='name')
        self.description = parse_str(data.get('description'), field='description')


class InstallmentEntity():
    def __init__(self, data: dict):
        self.due_date = parse_date(data.get("due_date"), field="due_date")
        self.amount = parse_float(data.get("amount"), field="amount", min_value=0.01)
        self.paid_amount = parse_float(data.get("paid_amount", 0.0), field="paid_amount", min_value=0)

        if self.paid_amount > self.amount:
            raise ValidationError("El monto pagado no puede ser mayor al valor total de la cuota.")


class PaymentPlanEntity():
    def __init__(self, data: dict):
        self.sale_order_id = parse_int(data.get("sale_order_id"), field="sale_order_id")
        self.payment_method_id = parse_int(data.get("payment_method_id"), field="payment_method_id")
        self.total_amount = parse_float(data.get("total_amount"), field="total_amount", min_value=0.01)
        self.total_installments = parse_int(data.get("total_installments", None), field="total_installments", nullable=True)

        # Validar existencia de sale_order y método de pago
        self.sale_order = SaleOrderService.get_obj(self.sale_order_id)
        from .services import PaymentMethodService
        self.payment_method = PaymentMethodService.get_obj(self.payment_method_id)

        # Cuotas (opcional en PATCH, obligatorias en POST)
        self.installments_data = data.get("installments", [])
        self.installments = []

        if not isinstance(self.installments_data, list):
            raise ValidationError("El campo 'installments' debe ser una lista de cuotas.")

        total_installment_sum = 0.0
        for inst_data in self.installments_data:
            inst = InstallmentEntity(inst_data)
            self.installments.append(inst)
            total_installment_sum += inst.amount

        if self.installments and round(total_installment_sum, 2) != round(self.total_amount, 2):
            raise ValidationError("La suma de las cuotas no coincide con el monto total del plan de pago.")


class PaymentTransactionEntity():
    def __init__(self, data: dict):
        self.payment_plan_id = parse_int(data.get("payment_plan_id"), field="payment_plan_id")
        self.installment_id = parse_int(data.get("installment_id"), field="installment_id", nullable=True)
        self.amount = parse_float(data.get("amount"), field="amount", min_value=0.01)
        self.payment_date = parse_date(data.get("payment_date"), field="payment_date", default=date.today())
        self.method_id = parse_int(data.get("method_id"), field="method_id", nullable=True)
        self.user_id = parse_int(data.get("user_id"), field="user_id", nullable=True)
        self.notes = parse_str(data.get("notes"), field="notes", nullable=True)

        # Validaciones clave
        from .services import PaymentPlanService
        from .services import InstallmentService

        self.plan = PaymentPlanService.get_obj(self.payment_plan_id)

        self.installment = None
        if self.installment_id:
            self.installment = InstallmentService.get_obj(self.installment_id)
            if self.installment.payment_plan_id != self.payment_plan_id:
                raise ValidationError("La cuota no pertenece al plan de pago indicado.")
