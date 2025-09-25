from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, getcontext

from flask import current_app

from app import db

from ..common.utils import validate_foreign_key
from ..core.enums import OrderStatus
from ..core.exceptions import ConflictError, NotFoundError, ValidationError
from ..core.filters import apply_filters
from .dto import (
    SaleOrderCreateDTO,
    SaleOrderPatchDTO,
    SaleOrderPreviewDTO,
    UpdateSaleOrderStatusDTO,
)
from .entities import SalesOrderEntity
from .models import SaleOrder, SaleOrderLine, SaleOrderPreview, SaleOrderPreviewLine

getcontext().rounding = ROUND_HALF_UP
CENT = Decimal("0.01")


class SalesOrderService:

    @staticmethod
    def create_obj(data):
        with db.session.begin():
            dto = SaleOrderCreateDTO.validate_with_message(**data)

            order = SalesOrderService.create_order(dto)
            return order

    @staticmethod
    def create_order(dto: SaleOrderCreateDTO):

        # Validar claves foráneas (no lo hace la entidad)
        from ..admin.models import Worker
        from ..common.models import AppSetting
        from ..crm.models import Cantons, Client, Provinces
        from ..products.models import ProductVariant

        validate_foreign_key(Client, dto.client_id, "Cliente")
        validate_foreign_key(Worker, dto.sales_person_id, "Vendedor")
        validate_foreign_key(Provinces, dto.shipping_province_id, "Provincia")
        validate_foreign_key(Cantons, dto.shipping_canton_id, "Canton")
        province = Provinces.query.get(dto.shipping_province_id)
        canton = Cantons.query.get(dto.shipping_canton_id)
        if canton not in province.cantons:
            raise ValueError("El canton no pertence  la provincia especificada")

        for line in dto.lines:
            validate_foreign_key(ProductVariant, line.variant_id, "Variante")

        tax_rate = AppSetting.query.filter(AppSetting.key == "tax_rate").first()
        if tax_rate is None:
            raise ValueError("No se ha registrao el IVA contacte al administrador")
        tax_rate = Decimal(tax_rate.value)

        # Crear modelo de orden (aquí mismo)
        order = SaleOrder(
            order_number=dto.order_number,
            order_date=dto.order_date or datetime.today(),
            due_date=dto.due_date,
            shipping_address=dto.shipping_address,
            shipping_province_id=dto.shipping_province_id,
            shipping_canton_id=dto.shipping_canton_id,
            shipping_reference=dto.shipping_reference,
            status=OrderStatus.PENDING.value,
            client_id=dto.client_id,
            sales_person_id=dto.sales_person_id,
            discount_rate=dto.discount_rate or Decimal("0.00"),
            tax_rate=tax_rate,
            notes=dto.notes,
            amount_paid=Decimal("0.00"),
            amount_due=Decimal("0.0"),
        )
        db.session.add(order)

        # Crear líneas y agregar
        for line_data in dto.lines:
            variant = ProductVariant.query.get(line_data.variant_id)
            if not variant:
                raise ValidationError(
                    f"No existe la variente con el id: {line_data.variant_id}"
                )
            line = SaleOrderLine(
                order=order,
                variant_id=line_data.variant_id,
                quantity=line_data.quantity,
                price_unit=variant.design.current_price,
                discount_rate=Decimal("0.00"),
            )
            db.session.add(line)

        # Lógica de negocio: cálculos
        entity = SalesOrderEntity(order, tax_rate)
        print(f"entity: {entity}, vs entiny.amount.paid {entity.order.amount_paid}")
        order.subtotal = entity.calculate_subtotal()
        base = entity.calculate_base()
        order.tax = entity.calculate_taxes(base)
        # discount = entity.calculate_total_discount()
        order.total = entity.calculate_total()
        order.subtotal = entity.calculate_subtotal()
        order.total = entity.calculate_total()
        order.amount_due = entity.calculate_total()
        print(f"order.amountpaid: {order.amount_paid}")

        print(f"TOtal de la orden:{order.total}")

        print(repr(order.total))
        print(order.total == Decimal("16.10"))
        # crear pago
        from ..payments.models import PaymentMethod, PaymentTransaction

        payment = dto.payment.amount.quantize(CENT)
        print(
            f" payment {payment} {type(payment)} vs total:{order.total} {type(order.total)}"
        )

        if payment > order.total:
            print("es aqui")
            raise ValidationError("El monto excede el total de la orden")
        payment_method = PaymentMethod.query.get(dto.payment.method_id)
        if payment_method is None:
            raise ValidationError("El metodo de pago seleccionado no existe")

        transaction = PaymentTransaction(
            sale_order=order,
            amount=dto.payment.amount,
            payment_date=dto.payment.date,
            user_id=None,
        )
        db.session.add(transaction)

        entity.order.amount_due = entity.calculate_total()

        entity.add_payment(dto.payment.amount)
        order.amount_paid = entity.order.amount_paid
        order.amount_due = entity.order.amount_due
        order.payment_status = entity.order.payment_status

        return order

    @staticmethod
    def delete_line(order_id: int, line_id: int):
        order = SalesOrderService.get_obj(order_id)
        if order.status != OrderStatus.DRAFT.value:
            raise ValidationError("Solo se pueden modificar órdenes en estado 'draft'.")

        line = SaleOrderLine.query.filter_by(id=line_id, sale_order_id=order.id).first()
        if not line:
            raise NotFoundError(f"Línea {line_id} no encontrada en esta orden.")

        db.session.delete(line)
        SalesOrderService.recalculate_totals(order)
        db.session.commit()

    @staticmethod
    def cancel_obj(order_id: int, reason: str):
        order = SalesOrderService.get_obj(order_id)

        if order.status == OrderStatus.CANCELED.value:
            raise ValidationError("La orden ya está cancelada.")

        if order.status == OrderStatus.DRAFT.value:
            raise ValidationError(
                "Una orden en estado draft puede eliminarse directamente."
            )

        order.status = OrderStatus.CANCELED.value
        order.canceled_reason = reason.strip() if reason else "Sin motivo registrado"
        db.session.commit()
        return order

    # @staticmethod
    # def delete_obj(order):

    # if order.status != OrderStatus.DRAFT.value:
    #  raise ValidationError("Solo se puede eliminar una orden en estado 'draft'.")

    # db.session.delete(order)
    # db.session.commit()

    @staticmethod
    def preview_order(data):
        # parsear DTO
        dto = SaleOrderPreviewDTO(**data)
        from ..common.models import AppSetting
        from ..products.models import ProductVariant

        tax_rate = AppSetting.query.filter(AppSetting.key == "tax_rate").first()
        if tax_rate is None:
            raise ValueError("No se ha registrao el IVA contacte al administrador")
        tax_rate = Decimal(tax_rate.value)

        # Crear modelo de preview (en memoria)
        preview_lines = []

        for line in dto.lines:
            variant = ProductVariant.query.get(line.variant_id)
            if not variant:
                raise ValidationError(
                    f"No existen variantes con el id: {str(line.variant_id)}"
                )

            prev_line = SaleOrderPreviewLine(
                variant_id=line.variant_id,
                quantity=line.quantity,
                # Obtenemos el precio actual desde backend para evitar inconsistencias y garantizar trazabilidad
                price_unit=Decimal(variant.design.current_price),
                discount_rate=line.discount_rate or Decimal("0.0"),
            )
            preview_lines.append(prev_line)

        preview_order = SaleOrderPreview(
            lines=preview_lines,
            discount_rate=dto.discount_rate or Decimal("0.0"),
            tax_rate=tax_rate,
        )

        print(preview_order)

        # Usar entidad para cálculos
        entity = SalesOrderEntity(preview_order, tax_rate)

        subtotal = entity.calculate_subtotal()
        base = entity.calculate_base()
        taxes = entity.calculate_taxes(base)
        discount = entity.calculate_total_discount()
        total = entity.calculate_total()

        return {
            "subtotal": subtotal,
            "base": base,
            "taxes": taxes,
            "discount": discount,
            "total": total,
        }

    @staticmethod
    def get_obj(order_id):
        order = SaleOrder.query.get(order_id)
        if not order:
            raise NotFoundError("Orden de venta no encontrada.")
        return order

    @staticmethod
    def get_obj_list(filters=None):
        """
        Obtiene lista de SaleOrders usando filtros dinámicos.
        """
        return apply_filters(SaleOrder, filters or {})

    @staticmethod
    def patch_obj(order, data):

        # parsear datos
        dto = SaleOrderPatchDTO(**data)
        updated_order = SalesOrderService.update_sale_order(order, dto)
        try:
            db.session.commit()
            return updated_order
        except Exception:
            db.session.rollback()
            current_app.logger.warning("Error al actualizar el elemento")
            raise

    @staticmethod
    def update_status_order(order, data):
        dto = UpdateSaleOrderStatusDTO(**data)
        print(f"si hay orden; {order.status}")
        print(f"SI ha dto: {dto.status}")
        if dto.status == "Aprobada":
            order.status = OrderStatus.APPROVED.value
            from ..core.enums import ProductionSourceTypeEnum
            from ..production.production_request_services import (
                ProductionRequestServices,
            )

            ProductionRequestServices.create_production_request(
                origin_type=ProductionSourceTypeEnum.SALES.value,
                origin_id=order.id,
                title="Ventas",
            )
        if dto.status == "Pendiente":
            order.status = OrderStatus.PENDING.value
        if dto.status == "Cancelada":

            order.status = OrderStatus.CANCELED.value
        if dto.status == "Rechazada":
            order.status == OrderStatus.REJECTED.value

        try:
            db.session.commit()
            return "Estado actualizado"
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            raise e

    @staticmethod
    def update_sale_order(order, dto):

        from ..products.models import ProductVariant

        # No permitir cambios si está aprobada o más adelante
        if order.status not in ("Borrador", "Pendiente"):
            raise ConflictError("La orden ya está aprobada y no puede editarse.")

        # Actualizar campos globales
        if dto.delivery_date is not None:
            order.delivery_date = dto.delivery_date
        if dto.delivery_address is not None:
            order.delivery_address = dto.delivery_address
        if dto.status is not None:
            order.status = dto.status.value
        if dto.discount is not None:
            order.discount = dto.discount
        if dto.tax is not None:
            order.tax = dto.tax
        if dto.notes is not None:
            order.notes = dto.notes

        # Actualizar líneas si vienen
        if dto.lines is not None:
            # Borrar las que no estén en el patch
            incoming_ids = [line.id for line in dto.lines if line.id]
            order.lines = [line for line in order.lines if line.id in incoming_ids]

            # Actualizar o agregar
            for line_data in dto.lines:
                variant = ProductVariant.query.get(line_data.variant_id)
                if not variant:
                    raise ValidationError(
                        f"No existe la variente con el id: {line_data.variant_id}"
                    )
                if line_data.id:
                    # Buscar línea existente
                    line = next(
                        (line for line in order.lines if line.id == line_data.id), None
                    )
                    if line:
                        line.variant_id = line_data.variant_id
                        line.quantity = line_data.quantity
                        # Obtenemos el precio actual desde backend para evitar inconsistencias y garantizar trazabilidad
                        line.price_unit = (variant.current_price,)
                        line.discount = line_data.discount or 0.0
                else:
                    # Nueva línea
                    new_line = SaleOrderLine(
                        variant_id=line_data.variant_id,
                        quantity=line_data.quantity,
                        # Obtenemos el precio actual desde backend para evitar inconsistencias y garantizar trazabilidad
                        price_unit=variant.current_price,
                        discount=line_data.discount or 0.0,
                    )
                    order.lines.append(new_line)

        # Recalcular totales
        entity = SalesOrderEntity(order)
        order.subtotal = entity.calculate_subtotal()
        order.total = entity.calculate_total()

        db.session.add(order)

        return order

    @staticmethod
    def delete_obj(order):
        """
        Borra la orden solo si está en 'draft' o 'pending_approval'.
        """
        print(f"order in service: {order}")
        if order.status not in ("Borrador", "Pendiente"):
            raise ConflictError(
                "La orden ya está aprobada o procesada y no se puede borrar."
            )

        try:
            db.session.delete(order)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f"Error al eliminar la orden. e:{e}")
            raise


class SaleOrderLineService:

    @staticmethod
    def get_order_list(order_id):
        order = SaleOrder.query.get(order_id)
        if order is None:
            raise NotFoundError(f"No existe orden de venta con id: {order_id}")
        lines = SaleOrderLine.query.filter(
            SaleOrderLine.sale_order_id == order_id
        ).all()

        return lines
