from flask import current_app
from app import db
from collections import defaultdict
from ..core.exceptions import ValidationError, NotFoundError
from ..core.origin_factory import OriginFactory
from ..core.filters import apply_filters
from ..common.utils import get_next_sequence_number
from .entities import (
    ProductionRequestEntity, 
    ProductionOrderEntity, 
    ProductionOrderLineEntity, 
    ProductionMaterialDetailEntity,
    )   

from .models import (
    ProductionRequest,
    ProductionOrder,
    ProductionOrderLine,
    ProductionCheckpoint,
    ProductionMaterialDetail,
    ManHourEstimate,
    ProductionRework,
    ProductionMaterialDetailForRework,
    ProductionMaterialSummary
)

from ..products.models import ProductVariantMaterialDetail

from .dto import ProductionOrderCreateDTO, ProductionOrderLineDTO

from ..core.enums import OrderStatus

from datetime import datetime, date

# ===================== SERVICES =====================
class ProductionOrderService:

    @staticmethod
    def get_obj(id):
        order = ProductionOrder.query.get(id)
        if not order:
            raise NotFoundError('o')
        return order
    
    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductionOrder, filters)
    
    @staticmethod
    def delete_obj(obj):
        try:
            db.session.delete(obj)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError("no")

    @staticmethod
    def create_obj(data: dict) -> ProductionOrder:
        """Entry point principal: maneja la transacción y la conversión de DTO."""
        with db.session.begin():
            dto = ProductionOrderCreateDTO(**data)
            order = ProductionOrderService.create_production_order(
                production_request_ids=dto.production_request_ids,
                workers_assigned=dto.workers_available,
                lines=dto.lines,   
            )

            return order

    @staticmethod
    def create_production_order(production_request_ids: list,
                                workers_assigned: float,
                                lines: list,
                                start_date: date,
                                end_date=None) -> ProductionOrder:
        """Función orquestadora principal: consolida, calcula y crea la orden.
            Lógica principal de creación de orden de producción.
        """
        code = ProductionOrderService._order_code_generator()

        # Crear objeto ProductionOrder
        order = ProductionOrder(
            code = code,
            start_date = start_date,
            workers_assigned=workers_assigned, 
            end_date = end_date          
        )
        db.session.add(order)
       
        # Asociar ProductionRequests y actualizar estado
        for req_id in production_request_ids:
            req = db.session.get(ProductionRequest, req_id)
            if not req:
                raise ValidationError(f'No existe un requerimiento con el id: {req_id}')
            req.status = OrderStatus.PLANNED.value
            order.production_requests.append(req)

        # Crear líneas de producción
        production_lines = ProductionOrderLineService.create_order_lines(order, lines)
        db.session.add_all(production_lines)

        db.session.flush() 
        # Calcular materiales requeridos (detalles por linea)
        material_details = ProductionMaterialService.calculate_line_materials(order)
        db.session.add_all(material_details)

        material_summary = ProductionMaterialService.create_material_summary(order)
        db.session.add_all(material_summary)

        return order
    
    @staticmethod
    def _order_code_generator():
        next_number = get_next_sequence_number(sequence_key='production_order_seq')
        next_code = f"OP-{next_number:03d}"
        return next_code


class ProductionOrderLineService:

    @staticmethod
    def create_order_lines(order:ProductionOrder, dto_lines:ProductionOrderLineDTO)->list[ProductionOrderLine]:
        """Define lineas para una orden de produccion
            Recibe la orden de produccion y las lineas
            Devuelve un lista de ordenes de produccion"""
        # Consolidar líneas de producción por variante
        consolidated_lines = ProductionOrderLineService._consolidate_lines(dto_lines)
        production_lines = []
        for line in consolidated_lines:
            new_line = ProductionOrderLine(
                production_order=order,
                product_variant_id=line['product_variant_id'],
                quantity=line['quantity'],
                workers_assigned=order.workers_assigned or 1,
                overtime_hours=order.total_overtime_hours or 0
            )

            estimated_time = ProductionOrderLineEntity(new_line).estimated_man_hours()
            new_line.estimated_man_hours = estimated_time
            
            production_lines.append(new_line)

        return production_lines
        

    @staticmethod
    def _consolidate_lines(raw_lines: list[ProductionOrderLineDTO]) -> list[dict]:
        """Consolida las lineas de produccion. Unifica a las mismas variantes en una linea misma linea. """
        from ..products.services import VariantService
        consolidated = defaultdict(float) # Usar defaultdict simplifica
        for line_dto in raw_lines: # Cambié 'line' a 'line_dto' para mayor claridad
            # Validar la existencia de la variante ANTES de intentar usar su ID
            variant = VariantService.get_obj(line_dto.product_variant_id)
            if not variant: # Esta validación ya la tienes, ¡bien!
                raise ValidationError(f'La variante del producto con el ID: {line_dto.product_variant_id} no existe')
            
            consolidated[line_dto.product_variant_id] += line_dto.quantity

        return [
            {"product_variant_id": variant_id, "quantity": qty}
            for variant_id, qty in consolidated.items()
        ]
    

class ProductionMaterialService:

    def calculate_line_materials(order: ProductionOrder) -> list[ProductionMaterialDetail]:
        """
        Calcula los materiales requeridos a nivel de detalle para una linea de producción.
        Crea objetos ProductionMaterialDetail 
        Devuelve una lista de Objetos ProductionMAterialDetail
        """
        material_details = []
        from ..products.services import VariantService, ProductVariantMaterialService
        for line in order.lines:
            variant = VariantService.get_obj(line.product_variant_id)
            bom = ProductVariantMaterialService.get_obj_list_by_variant(variant.id)

            for bom_item in bom:
                base_qty = bom_item.quantity * line.quantity

                detail = ProductionMaterialDetail(
                    order_line_id=line.id,
                    material_id=bom_item.material_id,
                    quantity_needed=base_qty,
                    waste_percentage=0.05,
                    quantity_reserved=0,
                    quantity_delivered=0,
                )
                total_qty = ProductionMaterialDetailEntity(detail).total_quantity_needed()
                detail.quantity_needed = total_qty
                material_details.append(detail)

        return material_details



    @staticmethod
    def create_material_summary(order: ProductionOrder)->list[ProductionMaterialSummary]:
        """
        Calcula el resumen total de materiales de la orden.
        Suma materiales de todas las líneas.
        Devuelve una lista de objetos ProductionMaterialSummary
        """
        summary = ProductionOrderEntity(order).calculate_material_summary()

        # Elimina las existentes para evitar duplicados o mantener la consistencia
        order.material_summaries.clear()
        production_material_summary = []
        for mat_id, total_qty in summary.items():
            material_summary = ProductionMaterialSummary(
                production_order=order,
                material_id=mat_id,
                total_quantity_needed=total_qty,
                quantity_reserved=0.0,
                quantity_pending=total_qty
            )
            production_material_summary.append(material_summary)

        return production_material_summary
