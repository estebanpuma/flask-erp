from flask import current_app
from app import db
from ..core.exceptions import ValidationError, NotFoundError
from ..core.origin_factory import OriginFactory
from ..common.parsers import parse_str, parse_int, parse_float
from ..core.filters import apply_filters
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



# Entities como estaban definidos antes...
# (El código de las entidades se mantiene igual que en la última actualización)

# ===================== SERVICES =====================

class ProductionRequestService:
    @staticmethod
    def create_obj(data: dict) -> ProductionRequest:
        entity = ProductionRequestEntity(data)
        instance = entity.to_model()
        db.session.add(instance)
        db.session.commit()
        return instance

    @staticmethod
    def get_obj(request_id: int) -> ProductionRequest:
        instance = ProductionRequest.query.get(request_id)
        if not instance:
            raise NotFoundError("Solicitud de producción no encontrada.")
        return instance
    
    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductionRequest, filters)


class ProductionOrderService:

    @staticmethod
    def create_obj(data: dict) -> ProductionOrder:
        entity = ProductionOrderEntity(data)
        order = entity.to_model()
        db.session.add(order)
        db.session.flush()  # Para obtener order.id

        for line in entity.get_lines(order.id):
            db.session.add(line)
            db.session.flush()
            ProductionMaterialExplosionService.explode_for_order_line(line)

        ProductionOrderEntity.calculate_total_man_hours(order)
        ProductionMaterialSummaryService.generate_summary_for_order(order)
        try:
            db.session.commit()
            return order
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'Error al crear la orden de producsion. e:{e}')
            raise

    @staticmethod
    def get_obj(order_id: int) -> ProductionOrder:
        instance = ProductionOrder.query.get(order_id)
        if not instance:
            raise NotFoundError("Orden de producción no encontrada.")
        return instance
    

    @staticmethod
    def get_obj_list(filters=None):
        from .models import ProductionOrder
        return apply_filters(ProductionOrder, filters)
    
    @staticmethod
    def delete_obj(obj):
        try:
            db.session.delete(obj)
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.warning(f'No se puede borrar la orden de produccion. e:{e}')
            raise

    @staticmethod
    def calculate_total_man_hours(order: ProductionOrder):
        total = sum([line.estimated_hours or 0 for line in order.lines])
        order.total_man_hours = total




class ProductionMaterialExplosionService:
    @staticmethod
    def explode_for_order_line(order_line: ProductionOrderLine):
        from ..products.models import ProductVariantMaterialDetail
        # obtener BOM del producto
        bom_items = ProductVariantMaterialDetail.query.filter_by(product_id=order_line.product_variant.product_id).all()

        if not bom_items:
            raise ValidationError("El producto no tiene materiales definidos en su BOM.")

        for bom_item in bom_items:
            quantity = ProductionMaterialDetailEntity.calculate_total_needed(
                base_quantity=order_line.quantity,
                base_material_qty=bom_item.quantity,
                waste_percentage=bom_item.waste_percentage
            )
            material_detail = ProductionMaterialDetail(
                order_line_id=order_line.id,
                material_id=bom_item.material_id,
                quantity_needed=quantity,
                waste_percentage=bom_item.waste_percentage
            )
            db.session.add(material_detail)
    
    @staticmethod
    def get_obj(id):
        bom = ProductionMaterialDetail.query.get(id)
        if not bom:
            raise NotFoundError('NO se encuentra el detalle de materiales')

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductionMaterialDetail, filters)


class ProductionMaterialSummaryService:
    @staticmethod
    def generate_summary_for_order(order: ProductionOrder):
        from sqlalchemy import func

        # Obtener suma por material_id desde los detalles de las líneas
        results = db.session.query(
            ProductionMaterialDetail.material_id,
            func.sum(ProductionMaterialDetail.quantity_needed)
        ).join(ProductionOrderLine).filter(
            ProductionOrderLine.production_order_id == order.id
        ).group_by(ProductionMaterialDetail.material_id).all()

        # Eliminar resumen anterior si existe (por regeneración)
        db.session.query(ProductionMaterialSummary).filter_by(production_order_id=order.id).delete()

        for material_id, total_quantity in results:
            summary = ProductionMaterialSummary(
                production_order_id=order.id,
                material_id=material_id,
                total_quantity_needed=round(total_quantity, 3),
                quantity_reserved=0.0,
                quantity_pending=round(total_quantity, 3)  # inicialmente todo está pendiente
            )
            db.session.add(summary)

        db.session.commit()
        return True
    
    @staticmethod
    def get_obj(id):
        summary = ProductionMaterialSummary.query.get(id)
        if not summary:
            raise NotFoundError("BOM no encontrado")
        
    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductionMaterialSummary, filters)
    

class ProductionCheckpointService:
    @staticmethod
    def complete_checkpoint(order_line_id: int, stage: str) -> ProductionCheckpoint:
        order_line = ProductionOrderLine.query.get(order_line_id)
        if not order_line:
            raise NotFoundError("Línea de producción no encontrada.")

        from .entities import ProductionCheckpointEntity
        ProductionCheckpointEntity.validate_stage_progression(order_line, stage)

        checkpoint = ProductionCheckpoint.query.filter_by(order_line_id=order_line_id, stage=stage).first()

        if not checkpoint:
            checkpoint = ProductionCheckpoint(order_line_id=order_line_id, stage=stage)
            db.session.add(checkpoint)

        checkpoint.completed = True
        checkpoint.completed_at = db.func.now()

        db.session.commit()
        return checkpoint
    
    @staticmethod
    def get_obj(id):
        checkpoint = ProductionCheckpoint.query.get(id)
        if not checkpoint:
            raise NotFoundError('No existe')
    
    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductionCheckpoint, filters)


class ProductionReworkService:
    @staticmethod
    def create_obj(data: dict) -> ProductionRework:
        from .entities import ProductionReworkEntity, ProductionMaterialDetailForReworkEntity

        rework_entity = ProductionReworkEntity(data)
        rework = rework_entity.to_model()
        db.session.add(rework)
        db.session.flush()  # Necesario para obtener rework_id

        materials_data = data.get("materials", [])
        for mat in materials_data:
            mat_entity = ProductionMaterialDetailForReworkEntity({
                **mat,
                "rework_id": rework.id
            })
            db.session.add(mat_entity.to_model())

        db.session.commit()
        return rework
    
    @staticmethod
    def get_obj(id):
        rework = ProductionRework.query.get(id)
        if not rework:
            raise NotFoundError('No existe el retrabajo')
    
    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductionRework, filters)