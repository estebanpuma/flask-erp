from app import db

from flask import current_app

from .models import SaleOrder, SaleOrderLine

from .entities import SaleOrderEntity, SaleOrderLineEntity

from ..core.enums import OrderStatus

from ..core.exceptions import NotFoundError, ValidationError

from ..core.filters import apply_filters

from ..common.parsers import parse_int, parse_float, parse_date, parse_enum, parse_str



class SaleOrderService:

    @staticmethod
    def get_obj(order_id: int) -> SaleOrder:
        obj = SaleOrder.query.get(order_id)
        if not obj:
            raise NotFoundError(f"Orden de venta {order_id} no encontrada.")
        return obj
    
    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(SaleOrder, filters)

    @staticmethod
    def create_obj(data: dict) -> SaleOrder:
        entity = SaleOrderEntity(data)

        sale_order = SaleOrder(
            order_number=entity.order_number,
            order_date=entity.order_date,
            delivery_date=entity.delivery_date,
            delivery_address=entity.delivery_address,
            status=entity.status.value,
            client_id=entity.client_id,
            sales_person_id=entity.sales_person_id,
            discount=entity.discount,
            tax=entity.tax,
        )

        db.session.add(sale_order)
        db.session.flush()

        subtotal = 0.0
        lines = []
        for line_entity in entity.lines:
            line = SaleOrderLine(
                sale_order_id=sale_order.id,
                variant_id=line_entity.variant_id,
                quantity=line_entity.quantity,
                price_unit=line_entity.price_unit,
                discount=line_entity.discount,
                cost_unit=line_entity.variant.cost_unit if hasattr(line_entity.variant, 'cost_unit') else None
            )
            lines.append(line)
            subtotal += line.subtotal

        sale_order.subtotal = subtotal
        sale_order.total = subtotal - sale_order.discount + sale_order.tax

        db.session.add_all(lines)
        try:
            db.session.commit()
            return sale_order
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al crear orsen de venta. e:{e}')
            raise
    

    @staticmethod
    def patch_obj(order:SaleOrder, data: dict) -> SaleOrder:
        

        if order.status != OrderStatus.DRAFT.value:
            raise ValidationError("Solo se puede editar una orden en estado 'draft'.")

        # Campos editables de cabecera
        if 'order_date' in data:
            order.order_date = parse_date(data['order_date'])
        if 'delivery_date' in data:
            delivery_date = parse_date(data['delivery_date'])
            if delivery_date and delivery_date < order.order_date:
                raise ValidationError("La fecha de entrega no puede ser anterior a la fecha de la orden.")
            order.delivery_date = delivery_date
        if 'delivery_address' in data:
            order.delivery_address = parse_str(data['delivery_address'], field='delivery_address')
        if 'status' in data:
            new_status = parse_enum(data['status'], OrderStatus, field='status')
            order.status = new_status.value
        if 'discount' in data:
            order.discount = parse_float(data['discount'], field='discount', min_value=0)
        if 'tax' in data:
            order.tax = parse_float(data['tax'], field='tax', min_value=0)

        SaleOrderService.recalculate_totals(order)
        try:
            db.session.commit()
            return order
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al actualizar la orden de venta. e:{e}')
            raise


    @staticmethod
    def recalculate_totals(order: SaleOrder):
        subtotal = sum(line.subtotal for line in order.lines)
        order.subtotal = subtotal
        order.total = subtotal - order.discount + order.tax

    @staticmethod
    def patch_line(order_id: int, line_id: int, data: dict) -> SaleOrderLine:
        order = SaleOrderService.get_obj(order_id)
        if order.status != OrderStatus.DRAFT.value:
            raise ValidationError("Solo se pueden modificar líneas de órdenes en estado 'draft'.")

        line = SaleOrderLine.query.filter_by(id=line_id, sale_order_id=order.id).first()
        if not line:
            raise NotFoundError(f"Línea {line_id} no encontrada en esta orden.")

        # Validaciones mínimas: cantidad, precio, descuento
        if "quantity" in data:
            line.quantity = parse_int(data["quantity"], field="quantity", min_value=1)
        if "price_unit" in data:
            line.price_unit = parse_float(data["price_unit"], field="price_unit", min_value=0)
        if "discount" in data:
            line.discount = parse_float(data["discount"], field="discount", min_value=0)
            if line.discount > line.price_unit:
                raise ValidationError("El descuento no puede ser mayor que el precio unitario.")

        SaleOrderService.recalculate_totals(order)
        try:
            db.session.commit()
            return line
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al actualizar orden de venta. e:{e}')
            raise

    @staticmethod
    def add_line(order_id: int, data: dict) -> SaleOrderLine:
        order = SaleOrderService.get_obj(order_id)
        if order.status != OrderStatus.DRAFT.value:
            raise ValidationError("Solo se pueden modificar órdenes en estado 'draft'.")

        line_entity = SaleOrderLineEntity(data)

        existing = next((l for l in order.lines if l.variant_id == line_entity.variant_id), None)
        if existing:
            raise ValidationError("Este producto ya fue agregado a la orden. Edita la línea existente si deseas cambiar cantidad o precio.")


        line = SaleOrderLine(
            sale_order_id=order.id,
            variant_id=line_entity.variant_id,
            quantity=line_entity.quantity,
            price_unit=line_entity.price_unit,
            discount=line_entity.discount,
            cost_unit=line_entity.variant.cost_unit if hasattr(line_entity.variant, 'cost_unit') else None
        )

        db.session.add(line)
        db.session.flush()
        SaleOrderService.recalculate_totals(order)
        db.session.commit()
        return line

    @staticmethod
    def delete_line(order_id: int, line_id: int):
        order = SaleOrderService.get_obj(order_id)
        if order.status != OrderStatus.DRAFT.value:
            raise ValidationError("Solo se pueden modificar órdenes en estado 'draft'.")

        line = SaleOrderLine.query.filter_by(id=line_id, sale_order_id=order.id).first()
        if not line:
            raise NotFoundError(f"Línea {line_id} no encontrada en esta orden.")

        db.session.delete(line)
        SaleOrderService.recalculate_totals(order)
        db.session.commit()

    @staticmethod
    def cancel_obj(order_id: int, reason: str):
        order = SaleOrderService.get_obj(order_id)

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
