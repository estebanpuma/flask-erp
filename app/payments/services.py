from flask import current_app

from app import db

from ..core.exceptions import AppError, ConflictError, NotFoundError
from ..core.filters import apply_filters
from ..sales.entities import SalesOrderEntity
from .dto import PaymentAgreementCreateDTO, PaymentTransactionCreateDTO
from .models import PaymentAgreement, PaymentMethod, PaymentTransaction


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
        existing = PaymentMethod.query.filter_by(name=data["name"].strip()).first()
        if existing:
            raise ConflictError("Ya existe un método de pago con ese nombre.")

        method = PaymentMethod(
            name=data["name"].strip(), description=data.get("description")
        )

        db.session.add(method)
        try:
            db.session.commit()
            return method
        except:
            db.session.rollback()
            raise

    @staticmethod
    def patch_obj(instance, data):

        if "name" in data:
            name = data["name"].strip()
            existing = PaymentMethod.query.filter_by(name=name).first()
            if existing and instance:
                raise ConflictError("Ya existe un método de pago con ese nombre.")
            instance.name = name

        if "description" in data:
            instance.description = data["description"]

        try:
            db.session.commit()
        except:
            db.session.rollback()
            print("sera aqui")
            raise

        return instance

    @staticmethod
    def delete_obj(method):
        transaction_exist = PaymentTransaction.query.filter(
            PaymentTransaction.method_id == method.id
        ).first()
        if transaction_exist:
            raise ValueError(
                "No se puede eliminar el metodo porque esta asociado a un pago"
            )
        db.session.delete(method)
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            current_app.logger.warning("No se pudo borrar el metodo de pago")
            raise


class PaymentAgreementService:

    @staticmethod
    def create_obj(data: dict) -> PaymentAgreement:
        with db.session.begin():
            dto = PaymentAgreementCreateDTO(**data)
            agreement = PaymentAgreementService.create_payment_agreement(dto)
            return agreement

    def create_payment_agreement(dto: PaymentAgreementCreateDTO):
        from ..sales.models import SaleOrder

        order = SaleOrder.query.get(dto.sale_order_id)
        if not order:
            raise NotFoundError("La orden de venta no existe.")
        if order.status in ("Cancelada", "Cerrada", "Aprobada"):
            raise AppError(
                "No se pueden registrar acuerdos en órdenes cerradas o aprobadas."
            )

        # Validar que el nuevo acuerdo no exceda el total de la orden
        total_agreements = sum(a.amount for a in order.agreements)
        new_total = total_agreements + dto.amount
        if new_total > order.total:
            raise AppError(
                f"El monto total de las cuotas comprometidas excede el total de la orden. Monto maximo:{str(order.total-total_agreements)}"
            )

        agreement = PaymentAgreement(
            sale_order_id=dto.sale_order_id,
            amount=dto.amount,
            expected_date=dto.expected_date,
            method_id=dto.method_id,
            user_id=dto.user_id,
            notes=dto.notes,
        )
        db.session.add(agreement)
        return agreement

    @staticmethod
    def patch_obj(id: int, dto) -> PaymentAgreement:

        agreement = PaymentAgreement.query.get(id)
        if not agreement:
            raise NotFoundError("El acuerdo no existe.")
        order = agreement.sale_order

        if order.status in ("Cancelada", "Cerrada"):
            raise AppError(
                "No se pueden modificar acuerdos en órdenes aprobadas o cerradas."
            )

        # Validar nuevo total de acuerdos si cambia el monto
        if dto.amount:
            total_agreements = sum(
                a.amount for a in order.agreements if a.id != agreement.id
            )
            new_total = total_agreements + dto.amount
            if new_total > order.total:
                raise AppError(
                    "El nuevo monto total de cuotas comprometidas excede el total de la orden."
                )
            agreement.amount = dto.amount

        if dto.expected_date:
            agreement.expected_date = dto.expected_date
        if dto.method_id:
            agreement.method_id = dto.method_id
        if dto.notes:
            agreement.notes = dto.notes
        if dto.user_id:
            agreement.user_id = dto.user_id

        try:
            db.session.add(agreement)
            db.session.commit()
            return agreement
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f"No se pudo actualizar cuota. e:{e}")
            raise

    @staticmethod
    def delete_obj(agreement):

        order = agreement.sale_order

        if order.status in ("canceled", "closed", "approved"):
            raise AppError(
                "No se pueden eliminar acuerdos de órdenes aprobadas o cerradas."
            )
        try:
            db.session.delete(agreement)
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.warning("No se pudo borrar la cuota")
            raise

    @staticmethod
    def get_obj(id: int) -> PaymentAgreement:
        agreement = PaymentAgreement.query.get(id)
        if not agreement:
            raise NotFoundError("La cuota no existe.")
        return agreement

    @staticmethod
    def get_obj_list(filters: None) -> list[PaymentAgreement]:
        return apply_filters(PaymentAgreement, filters)

    @staticmethod
    def get_sale_agreements(id):
        from ..sales.models import SaleOrder

        sale = SaleOrder.query.get(id)
        if not sale:
            raise NotFoundError(f"No existe la orden de venta con id:{str(id)}")
        return sale.agreements


class PaymentTransactionService:

    @staticmethod
    def create_obj(data: dict) -> PaymentTransaction:
        with db.session.begin():
            dto = PaymentTransactionCreateDTO(**data)
            transaction = PaymentTransactionService.create_payment_transaction(dto)
            return transaction

    @staticmethod
    def create_payment_transaction(dto):
        from ..sales.models import SaleOrder
        from .models import PaymentTransaction

        order = SaleOrder.query.get(dto.sale_order_id)
        if not order:
            raise NotFoundError("La orden de venta no existe.")
        if order.status in ("Cancelada", "Cerrada"):
            raise AppError(
                "No se pueden registrar pagos en órdenes canceladas o cerradas."
            )

        # Crear el pago
        payment = PaymentTransaction(
            sale_order_id=dto.sale_order_id,
            amount=dto.amount,
            payment_date=dto.payment_date,
            method_id=dto.method_id,
            user_id=dto.user_id,
            notes=dto.notes,
        )
        db.session.add(payment)

        # Actualizar saldo y estado real (solo pagos reales)
        order_entity = SalesOrderEntity(order)
        order_entity.add_payment(dto.amount)

        return payment

    @staticmethod
    def patch_obj(payment: PaymentTransaction, dto) -> PaymentTransaction:

        order = payment.sale_order

        if order.status in ("Canceladas", "Cerradas"):
            raise AppError(
                "No se pueden modificar pagos en órdenes canceladas o cerradas."
            )

        if dto.amount:
            order_entity = SalesOrderEntity(order)
            # Revertir el pago anterior
            order_entity.remove_payment(payment.amount)
            # Aplicar el nuevo pago
            order_entity.add_payment(dto.amount)
            payment.amount = dto.amount

        if dto.payment_date:
            payment.payment_date = dto.payment_date
        if dto.method_id:
            payment.method_id = dto.method_id
        if dto.notes:
            payment.notes = dto.notes
        if dto.user_id:
            payment.user_id = dto.user_id

        try:
            db.session.commit()
            return payment
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f"No se pudo actualizar el pago. e:{e}")
            raise

    @staticmethod
    def delete_obj(payment: PaymentTransaction):

        order = payment.sale_order

        if order.status in ("canceled", "closed"):
            raise AppError(
                "No se pueden eliminar pagos en órdenes canceladas o cerradas."
            )

        # Revertir saldo real
        order_entity = SalesOrderEntity(order)
        order_entity.remove_payment(payment.amount)
        try:
            db.session.delete(payment)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            current_app.logger.warning("No se pudo borrar el pago")
            raise

    @staticmethod
    def get_obj(id: int) -> PaymentTransaction:
        payment = PaymentTransaction.query.get(id)
        if not payment:
            raise NotFoundError("El pago no existe.")
        return payment

    @staticmethod
    def get_obj_list(filters: dict = None) -> list[PaymentTransaction]:
        query = PaymentTransaction.query
        if "sale_order_id" in filters:
            query = query.filter_by(sale_order_id=filters["sale_order_id"])
            return query.all()
        if "user_id" in filters:
            query = query.filter_by(user_id=filters["user_id"])
            return query.all()
        if "from_date" in filters and "to_date" in filters:
            query = query.filter(
                PaymentTransaction.payment_date.between(
                    filters["from_date"], filters["to_date"]
                )
            )
            return query.all()
        else:
            return apply_filters(PaymentTransaction, filters)

    @staticmethod
    def get_sale_payments(id):
        from ..sales.models import SaleOrder

        sale = SaleOrder.query.get(id)
        if not sale:
            raise NotFoundError(f"No existe la orden de venta con id:{str(id)}")
        return sale.transactions
