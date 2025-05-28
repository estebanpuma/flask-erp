from app import db

from flask import current_app

from .models import SaleOrder, SaleOrderLine, SaleOrderPreview, SaleOrderPreviewLine

from .entities import SalesOrderEntity

from ..core.enums import OrderStatus

from ..core.exceptions import NotFoundError, ValidationError

from ..common.utils import validate_foreign_key

from ..core.filters import apply_filters

from ..common.parsers import parse_int, parse_float, parse_date, parse_enum, parse_str

from .dto import SaleOrderCreateDTO, SaleOrderPreviewDTO, SaleOrderPatchDTO

from ..core.exceptions import ConflictError


class SalesOrderService:

    @staticmethod
    def create_obj(data):
        with db.session.begin():
            dto = SaleOrderCreateDTO(**data)
            order = SalesOrderService.create_order(dto)
            return order
        
    @staticmethod
    def create_order(dto):
        
        # Validar claves foráneas (no lo hace la entidad)
        from ..crm.models import Client
        from ..admin.models import Salesperson
        from ..products.models import ProductVariant
        validate_foreign_key(Client, dto.client_id, "Cliente")
        validate_foreign_key(Salesperson, dto.sales_person_id, "Vendedor")

        for line in dto.lines:
            validate_foreign_key(ProductVariant, line.variant_id, "Variante")

        # Crear modelo de orden (aquí mismo)
        order = SaleOrder(
            order_number=dto.order_number,
            order_date=dto.order_date,
            delivery_date=dto.delivery_date,
            delivery_address=dto.delivery_address,
            status='Borrador',
            client_id=dto.client_id,
            sales_person_id=dto.sales_person_id,
            discount=dto.discount or 0.0,
            tax=dto.tax or 0.0,
            notes=dto.notes
        )
        db.session.add(order)

        # Crear líneas y agregar
        for line_data in dto.lines:
            variant = ProductVariant.query.get(line_data.variant_id)
            if not variant:
                raise ValidationError(f'No existe la variente con el id: {line_data.variant_id}')
            line = SaleOrderLine(
                variant_id=line_data.variant_id,
                quantity=line_data.quantity,
                price_unit=variant.current_price,
                discount=line_data.discount or 0.0
            )
            order.lines.append(line)

         # Lógica de negocio: cálculos 
        entity = SalesOrderEntity(order)
        order.subtotal = entity.calculate_subtotal()
        order.total = entity.calculate_total()

        order.amount_due = order.total

        #crear cuotas/acuerdos de pago
        new_total_installment = 0
        from ..payments.models import PaymentAgreement
        for agreement_data in dto.agreements:
            print(f'aber newTT:{new_total_installment} vs agrAM:{agreement_data.amount}')
            new_total_installment += agreement_data.amount
            print(f'Ahora si el total inst: {new_total_installment} vs {order.total}' )
            if new_total_installment > order.total:
                raise ValidationError(f"El monto total de las cuotas comprometidas excede el total de la orden. Monto maximo:{str(order.total-(new_total_installment-agreement_data.amount))}")

            agreement = PaymentAgreement(
                amount=agreement_data.amount,
                expected_date=agreement_data.expected_date,
                notes=agreement_data.notes,
                user_id=order.sales_person_id
            )
            order.agreements.append(agreement)  

       

        db.session.add(order)

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
            raise ValidationError("Una orden en estado draft puede eliminarse directamente.")

        order.status = OrderStatus.CANCELED.value
        order.canceled_reason = reason.strip() if reason else "Sin motivo registrado"
        db.session.commit()
        return order

    @staticmethod
    def delete_obj(order):
        
        if order.status != OrderStatus.DRAFT.value:
            raise ValidationError("Solo se puede eliminar una orden en estado 'draft'.")

        db.session.delete(order)
        db.session.commit()

    @staticmethod
    def preview_order(data):
        #parsear DTO
        dto = SaleOrderPreviewDTO(**data)
        print(f'dto in service: {dto}')
        from ..products.models import ProductVariant

        # Crear modelo de preview (en memoria)
        preview_lines = []

        for line in dto.lines:
            variant = ProductVariant.query.get(line.variant_id)
            if not variant:
                raise ValidationError(f'No existen variantes con el id: {str(line.variant_id)}')
            print(f'variant price: {variant.current_price}')
            prev_line = SaleOrderPreviewLine(
                variant_id=line.variant_id,
                quantity=line.quantity,
                # Obtenemos el precio actual desde backend para evitar inconsistencias y garantizar trazabilidad
                price_unit=variant.current_price,
                discount=line.discount or 0.0)
            preview_lines.append(prev_line)

        preview_order = SaleOrderPreview(
            lines=preview_lines,
            discount=dto.discount or 0.0,
            tax=dto.tax or 0.0
        )

        # Usar entidad para cálculos
        entity = SalesOrderEntity(preview_order)
        
   
        subtotal = entity.calculate_subtotal()
        total = entity.calculate_total()

       

        return {
            "subtotal": subtotal,
            "total": total
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
        
        #parsear datos
        dto = SaleOrderPatchDTO(**data)
        updated_order = SalesOrderService.update_sale_order(order, dto)
        try:
            db.session.commit()
            return updated_order
        except Exception:
            db.session.rollback()
            current_app.logger.warning('Error al actualizar el elemento')
            raise

    @staticmethod
    def update_sale_order(order, dto):
        
        from ..products.models import ProductVariant
        # No permitir cambios si está aprobada o más adelante
        if order.status not in ('Borrador', 'Pendiente'):
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
            order.lines = [
                line for line in order.lines
                if line.id in incoming_ids
            ]

            # Actualizar o agregar
            for line_data in dto.lines:
                variant = ProductVariant.query.get(line_data.variant_id)
                if not variant:
                    raise ValidationError(f'No existe la variente con el id: {line_data.variant_id}')
                if line_data.id:
                    # Buscar línea existente
                    line = next((l for l in order.lines if l.id == line_data.id), None)
                    if line:
                        line.variant_id = line_data.variant_id
                        line.quantity = line_data.quantity
                        # Obtenemos el precio actual desde backend para evitar inconsistencias y garantizar trazabilidad
                        line.price_unit=variant.current_price,
                        line.discount = line_data.discount or 0.0
                else:
                    # Nueva línea
                    new_line = SaleOrderLine(
                        variant_id=line_data.variant_id,
                        quantity=line_data.quantity,
                        # Obtenemos el precio actual desde backend para evitar inconsistencias y garantizar trazabilidad
                        price_unit=variant.current_price,
                        discount=line_data.discount or 0.0
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
        print(f'order in service: {order}')
        if order.status not in ('Borrador', 'Pendiente'):
            raise ConflictError("La orden ya está aprobada o procesada y no se puede borrar.")

        try:
            db.session.delete(order)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al eliminar la orden. e:{e}')
            raise