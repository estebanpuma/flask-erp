from .models import PaymentMethod, PaymentPlan, Installment, InstallmentStatus, PaymentTransaction
from flask import current_app
from app import db

from datetime import date

from ..common.parsers import parse_int, parse_float
from ..core.exceptions import *
from ..core.filters import apply_filters

from .entities import PaymentPlanEntity, InstallmentEntity, PaymentTransactionEntity


class PaymentMethodService:

    @staticmethod
    def get_obj_list(filters=None):
       
        return apply_filters(PaymentMethod, filters)
    

    @staticmethod
    def get_obj(id):
        method = PaymentMethod.query.get(id)
        return method


    @staticmethod
    def create_obj(data: dict):
        existing = PaymentMethod.query.filter_by(name=data['name'].strip()).first()
        if existing:
            raise ConflictError("Ya existe un método de pago con ese nombre.")

        method = PaymentMethod(name=data['name'].strip(), description=data.get('description'))

        db.session.add(method)
        try:
            db.session.commit()
            return method
        except:
            db.session.rollback()
            raise


    @staticmethod
    def patch_obj(instance, data):
        

        if 'name' in data:
            name = data['name'].strip()
            existing = PaymentMethod.query.filter_by(name=name).first()
            if existing and instance:
                raise ConflictError("Ya existe un método de pago con ese nombre.")
            instance.name = name

        if 'description' in data:
            instance.description = data['description']

        try:
            db.session.commit()
        except:
            db.session.rollback()
            print('sera aqui')
            raise

        return instance
    

    @staticmethod
    def delete_obj(resource_id):
        method = PaymentMethod.query.get(resource_id)
        if not method:
            raise NotFoundError("Método de pago no encontrado.")

        db.session.delete(method)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

        return True
    

class PaymentPlanService:   
    ###metodo de plan de pago PaymentMethod
    @staticmethod
    def get_obj(id):
        payment_plan = PaymentPlan.query.get(id)
        if not payment_plan:
            raise NotFoundError('Plan de pago no encontrado')
        return payment_plan
    
    @staticmethod
    def get_obj_list(filters=None):
        
        return apply_filters(PaymentPlan, filters)

    @staticmethod
    def create_obj(data: dict) -> PaymentPlan:
        entity = PaymentPlanEntity(data)

        plan = PaymentPlan(
            sale_order_id=entity.sale_order_id,
            payment_method_id=entity.payment_method_id,
            total_amount=entity.total_amount,
            total_installments=entity.total_installments,
        )
        db.session.add(plan)
        db.session.flush()  # Para obtener plan.id

        installments = []
        for inst in entity.installments:
            i = Installment(
                payment_plan_id=plan.id,
                due_date=inst.due_date,
                amount=inst.amount,
                paid_amount=inst.paid_amount,
                status="Paid" if inst.paid_amount >= inst.amount else "Pending"
            )
            installments.append(i)

        db.session.add_all(installments)
        db.session.commit()
        return plan
    
    @staticmethod
    def patch_obj(plan_id: int, data: dict) -> PaymentPlan:
        plan = PaymentPlanService.get_obj(plan_id)

        if "total_amount" in data:
            plan.total_amount = parse_float(data["total_amount"], field="total_amount", min_value=0.01)
        if "total_installments" in data:
            plan.total_installments = parse_int(data["total_installments"], field="total_installments", nullable=True)
        if "payment_method_id" in data:
            payment_method_id = parse_int(data["payment_method_id"], field="payment_method_id")
            PaymentMethodService.get_obj(payment_method_id)  # Validación
            plan.payment_method_id = payment_method_id

        db.session.commit()
        return plan

    @staticmethod
    def delete_obj(plan_id: int):
        plan = PaymentPlanService.get_obj(plan_id)

        # Si alguna cuota ya fue pagada, no se puede eliminar
        if any(i.paid_amount > 0 for i in plan.installments):
            raise ValidationError("No se puede eliminar un plan con cuotas ya abonadas.")

        db.session.delete(plan)
        db.session.commit()


class InstallmentService:

    @staticmethod
    def get_obj(installment_id: int) -> Installment:
        inst = Installment.query.get(installment_id)
        if not inst:
            raise NotFoundError(f"Installment {installment_id} not found.")
        return inst

    @staticmethod
    def recalcular_estado(inst: Installment):
        if inst.paid_amount == 0:
            inst.status = InstallmentStatus.PENDING.value
        elif inst.paid_amount < inst.amount:
            inst.status = InstallmentStatus.PARTIALLY_PAID.value
        else:
            inst.status = InstallmentStatus.PAID.value


class PaymentTransactionService:

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(PaymentTransaction, filters)

    @staticmethod
    def get_obj(id):
        method = PaymentTransaction.query.get(id)
        return method

    @staticmethod
    def create_obj(data: dict) -> PaymentTransaction:
        entity = PaymentTransactionEntity(data)

        transaction = PaymentTransaction(
            payment_plan_id=entity.payment_plan_id,
            installment_id=entity.installment_id,
            amount=entity.amount,
            payment_date=entity.payment_date,
            method_id=entity.method_id,
            user_id=entity.user_id,
            notes=entity.notes
        )

        db.session.add(transaction)

        # Si tiene cuota asociada → actualiza automáticamente su estado
        if entity.installment:
            inst = entity.installment
            inst.paid_amount += entity.amount
            inst.paid_on = entity.payment_date
            inst.user_id = entity.user_id
            InstallmentService.recalcular_estado(inst)

        db.session.commit()
        return transaction