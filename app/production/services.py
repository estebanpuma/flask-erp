from flask import current_app
from app import db
from ..core.exceptions import ValidationError, NotFoundError
from ..core.origin_factory import OriginFactory
from ..core.filters import apply_filters
from .entities import (
    ProductionRequestEntity, 
    ProductionOrderEntity, 
    ProductionOrderLineEntity, 
    #ProductionMaterialDetailEntity,
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

from .production_order_dto import ProductionOrderCreateDTO

# Entities como estaban definidos antes...
# (El código de las entidades se mantiene igual que en la última actualización)

# ===================== SERVICES =====================
class ProductionOrderService:

     
    @staticmethod
    def create_obj(dto: ProductionOrderCreateDTO)-> ProductionOrder:
        """Crea una nueva orden de produccion"""
        with db.session.begin():
            order = ProductionOrderService.create_production_order(dto)
            return order

    @staticmethod
    def create_production_order(dto: ProductionOrderCreateDTO) -> ProductionOrder:

        order = ProductionOrder(
            start_date=dto.start_date,
            end_date=dto.end_date,
            status="Planificado"
        )

        # Crea y asocia las líneas
        for line_dto in dto.lines:
            line = ProductionOrderLine(
                product_variant_id=line_dto.product_variant_id,
                quantity=line_dto.quantity,
                production_request_id=line_dto.production_request_id
            )
            order.lines.append(line)  # SQLAlchemy maneja todo

            # Calcula y asigna materiales automáticamente
            line_materials = ProductionOrderService._create_materials_for_line(line)

            print(line_materials)

        # Agrega la orden a la sesión
        db.session.add(order)

        return order

    @staticmethod
    def _create_materials_for_line(line: ProductionOrderLine):
        """
        Crea materiales necesarios automáticamente para la línea.
        Se asume que se llama dentro de una transacción activa.
        """
        bom = ProductVariantMaterialDetail.query.filter_by(
            product_variant_id=line.product_variant_id
        ).all()

        for material_detail in bom:
            material_needed = ProductionMaterialDetail(
                order_line_id=line.id,
                material_id=material_detail.material_id,
                quantity_needed=material_detail.quantity_per_unit * line.quantity,
                waste_percentage=5.0,
                quantity_reserved=0.0,
                quantity_delivered=0.0
            )
            line.materials.append(material_needed)

        return line.materials
    

    @staticmethod
    def create_material_summary(order: ProductionOrder):
        """
        Calcula el resumen total de materiales de la orden.
        Suma materiales de todas las líneas.
        """
        summary = {}
        for line in order.lines:
            for material in line.materials:
                mat_id = material.material_id
                qty = material.quantity_needed

                if mat_id in summary:
                    summary[mat_id] += qty
                else:
                    summary[mat_id] = qty

        for mat_id, total_qty in summary.items():
            material_summary = ProductionMaterialSummary(
                production_order_id=order.id,
                material_id=mat_id,
                total_quantity_needed=total_qty,
                quantity_reserved=0.0,
                quantity_pending=total_qty
            )
            db.session.add(material_summary)
