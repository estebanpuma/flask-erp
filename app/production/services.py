from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

from flask import current_app

from app import db

from ..common.utils import get_next_sequence_number
from ..core.enums import OrderStatus
from ..core.exceptions import NotFoundError, ValidationError
from ..core.filters import apply_filters
from .dto import (
    OperationDTO,
    OperationPatchDTO,
    OperationStatusDTO,
    ProductionOrderCreateDTO,
    ProductionOrderLineDTO,
)
from .dto_production_resources import ProductionResourceDTO, ProductionResourcePatchDTO
from .entities import (
    ProductionMaterialDetailEntity,
    ProductionOrderEntity,
    ProductionOrderLineEntity,
)
from .models import (
    Operations,
    ProductionMaterialDetail,
    ProductionMaterialSummary,
    ProductionOrder,
    ProductionOrderLine,
    ProductionRequest,
    ProductionResource,
    VariantOperationResource,
)


# ===================== SERVICES =====================
class ProductionOrderService:

    @staticmethod
    def get_obj(id):
        order = ProductionOrder.query.get(id)
        if not order:
            raise NotFoundError(f"Orden con ID:{id} no encontrada")
        return order

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductionOrder, filters)

    @staticmethod
    def delete_obj(obj: ProductionOrder) -> bool:
        if (
            obj.status == OrderStatus.WIP.value
            or obj.status == OrderStatus.DELIVERED.value
        ):
            raise ValidationError(
                "No se pueden borrar las ordenes entregadas o en proceso. Puede cancelarla"
            )

        requests = obj.production_requests

        for req in requests:
            req.status = OrderStatus.APPROVED.value
        try:
            db.session.delete(obj)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise ValueError("No se pudo borrar")

    @staticmethod
    def create_obj(data: dict) -> ProductionOrder:
        """Entry point principal: maneja la transacción y la conversión de DTO."""
        with db.session.begin():
            dto = ProductionOrderCreateDTO(**data)
            new_order = ProductionOrderService.create_production_order(
                production_request_ids=dto.production_request_ids,
                workers_assigned=dto.workers_available,
                total_overtime_hours=dto.total_overtime_hours or 0,
                start_date=dto.start_date,
                end_date=dto.end_date,
            )

            return new_order

    @staticmethod
    def create_production_order(
        production_request_ids: list,
        workers_assigned: int,
        total_overtime_hours: float,
        start_date: date,
        end_date=None,
    ) -> ProductionOrder:
        """Función orquestadora principal: consolida, calcula y crea la orden.
        Lógica principal de creación de orden de producción.
        """
        code = ProductionOrderService._order_code_generator()

        # Crear objeto ProductionOrder
        order = ProductionOrder(
            code=code,
            start_date=start_date,
            workers_assigned=workers_assigned,
            total_overtime_hours=total_overtime_hours,
            end_date=end_date,
        )
        db.session.add(order)

        # Asociar ProductionRequests linez y y actualizar estado
        dto_lines = []
        for req_id in production_request_ids:

            req = db.session.get(ProductionRequest, req_id)
            if not req:
                raise ValidationError(f"No existe un requerimiento con el id: {req_id}")
            if req.status != OrderStatus.APPROVED.value:
                raise ValidationError(
                    "Solo se pueden planificar requesiciones aprobadas"
                )
            req.status = OrderStatus.PLANNED.value
            order.production_requests.append(req)
            req_lines = ProductionOrderService.get_request_lines(req)
            dto_lines.extend(req_lines)

        # Crear líneas de producción
        production_lines = ProductionOrderLineService.create_order_lines(
            order, dto_lines
        )
        db.session.add_all(production_lines)

        print(f"pasado production lines: {order.lines}")
        order.estimated_man_hours = ProductionOrderEntity(order).total_man_hours
        print(f"pasado total estimated {order.estimated_man_hours}")
        # Calcular materiales requeridos (detalles por linea)
        material_details = ProductionMaterialService.calculate_line_materials(order)
        db.session.add_all(material_details)
        print("Pasado add materials")
        material_summary = ProductionMaterialService.create_material_summary(order)
        db.session.add_all(material_summary)
        print("pasadooooo Summary")
        return order

    @staticmethod
    def _order_code_generator():
        next_number = get_next_sequence_number(sequence_key="production_order_seq")
        year = datetime.today().year
        next_code = f"OP-{str(year)}-{next_number:03d}"
        return next_code

    @staticmethod
    def get_request_lines(req: ProductionRequest) -> list[ProductionOrderLineDTO]:
        lines = []
        origin = req.origin_obj
        origin_lines = origin.lines
        for line in origin_lines:
            raw_line = {
                "product_variant_id": line.variant_id,
                "quantity": line.quantity,
            }
            line = ProductionOrderLineDTO(**raw_line)
            lines.append(line)
        return lines


class ProductionOrderLineService:

    @staticmethod
    def get_obj(id):
        line = ProductionOrderLine.query.get(id)
        if not line:
            raise NotFoundError(f"No se encontro una linea con el ID: {str(id)}")
        return line

    @staticmethod
    def get_obj_list(filters=None):
        return apply_filters(ProductionOrderLine, filters)

    @staticmethod
    def get_obj_list_by_order(order_id):
        lines = ProductionOrderLine.query.filter(
            ProductionOrderLine.production_order_id == order_id
        ).all()
        return lines

    @staticmethod
    def create_order_lines(
        order: ProductionOrder, dto_lines: ProductionOrderLineDTO
    ) -> list[ProductionOrderLine]:
        """Define lineas para una orden de produccion
        Recibe la orden de produccion y las lineas
        Devuelve un lista de ordenes de produccion"""
        # Consolidar líneas de producción por variante
        consolidated_lines = ProductionOrderLineService._consolidate_lines(dto_lines)
        # reparto las horas extra globales/totales equitativamente para cada linea. Luego podra editarse
        total_lines = len(consolidated_lines)
        assigned_overtime_hours = (
            order.total_overtime_hours / total_lines if total_lines else 0
        )
        production_lines = []
        from ..products.services import VariantService

        for line in consolidated_lines:
            new_line = ProductionOrderLine(
                production_order=order,
                product_variant_id=line["product_variant_id"],
                quantity=line["quantity"],
                workers_assigned=order.workers_assigned or 0,
                overtime_hours=assigned_overtime_hours or 0,
            )
            variant = VariantService.get_obj(line["product_variant_id"])

            estimated_time = ProductionOrderLineEntity(new_line).estimated_man_hours(
                standar_time=variant.standar_time
            )

            new_line.estimated_man_hours = estimated_time

            production_lines.append(new_line)

        return production_lines

    @staticmethod
    def _consolidate_lines(raw_lines: list[ProductionOrderLineDTO]) -> list[dict]:
        """Consolida las lineas de produccion. Unifica a las mismas variantes en una linea misma linea."""
        from ..products.services import VariantService

        consolidated = defaultdict(float)  # Usar defaultdict simplifica
        for line_dto in raw_lines:  # Cambié 'line' a 'line_dto' para mayor claridad
            # Validar la existencia de la variante ANTES de intentar usar su ID
            variant = VariantService.get_obj(line_dto.product_variant_id)
            if not variant:  # Esta validación ya la tienes, ¡bien!
                raise ValidationError(
                    f"La variante del producto con el ID: {line_dto.product_variant_id} no existe"
                )

            consolidated[line_dto.product_variant_id] += line_dto.quantity

        return [
            {"product_variant_id": variant_id, "quantity": qty}
            for variant_id, qty in consolidated.items()
        ]


class ProductionMaterialService:

    @staticmethod
    def get_material_summary(order_id: int) -> list[ProductionMaterialSummary]:

        summary = ProductionMaterialSummary.query.filter(
            ProductionMaterialSummary.production_order_id == order_id
        ).all()
        return summary

    @staticmethod
    def get_line_materials(line_id: int) -> list[ProductionMaterialDetail]:

        materials = ProductionMaterialDetail.query.filter(
            ProductionMaterialDetail.order_line_id == line_id
        ).all()
        return materials

    @staticmethod
    def calculate_line_materials(
        order: ProductionOrder,
    ) -> list[ProductionMaterialDetail]:
        """
        Calcula los materiales requeridos a nivel de detalle para una linea de producción.
        Crea objetos ProductionMaterialDetail
        Devuelve una lista de Objetos ProductionMAterialDetail
        """
        material_details = []
        from ..products.services import ProductVariantMaterialService, VariantService

        for line in order.lines:
            variant = VariantService.get_obj(line.product_variant_id)
            bom = ProductVariantMaterialService.get_obj_list_by_variant(variant.id)
            print(f"this is the boom {bom} , {type(bom)}, {len(bom)}")
            for bom_item in bom:
                base_qty = bom_item.quantity * line.quantity
                print(f"base qty {base_qty}")
                detail = ProductionMaterialDetail(
                    order_line_id=line.id,
                    material_id=bom_item.material_id,
                    quantity_needed=base_qty,
                    waste_percentage=5.00,
                    quantity_reserved=0,
                    quantity_delivered=0,
                )
                total_qty = ProductionMaterialDetailEntity(detail).total_quantity_needed
                detail.quantity_needed = total_qty
                material_details.append(detail)

        return material_details

    @staticmethod
    def create_material_summary(
        order: ProductionOrder,
    ) -> list[ProductionMaterialSummary]:
        """
        Calcula el resumen total de materiales de la orden.
        Suma materiales de todas las líneas.
        Devuelve una lista de objetos ProductionMaterialSummary
        """
        summary = ProductionOrderEntity(order).calculate_material_summary

        # Elimina las existentes para evitar duplicados o mantener la consistencia
        order.material_summaries.clear()
        production_material_summary = []
        for mat_id, total_qty in summary.items():
            material_summary = ProductionMaterialSummary(
                production_order=order,
                material_id=mat_id,
                total_quantity_needed=total_qty,
                quantity_reserved=0.0,
                quantity_pending=total_qty,
            )
            production_material_summary.append(material_summary)

        return production_material_summary


class OperationService:

    @staticmethod
    def create_obj(data: dict) -> Operations:
        with db.session.begin():
            dto = OperationDTO(**data)
            op = OperationService.create_op(
                name=dto.name,
                goal=dto.goal,
                kpi=dto.kpi,
                # responsible = dto.responsible,
                job_id=dto.job_id,
            )

            return op

    @staticmethod
    def create_op(
        name: str,
        # code:str,
        # responsible:str,
        job_id,
        goal: str = None,
        kpi: str = None,
    ) -> Operations:
        from ..admin.models import Job

        job = Job.query.get(job_id)
        if not job:
            raise ValidationError(f"No existe el puesto de trabajo con ID: {job_id}")
        op_number = str(OperationService.get_next_number())
        code = f"P{op_number.zfill(3)}"
        op = Operations(
            name=name,
            code=code,
            responsible_id=job_id,
            goal=goal,
            kpi=kpi,
        )
        db.session.add(op)
        return op

    def get_next_number() -> int:
        from ..common.models import AppSetting

        prefix = "operation_code_counter"

        counter = AppSetting.query.filter(AppSetting.key == prefix).first()

        if counter:
            n = int(counter.value) + 1
            counter.value = n
            return int(n)
        else:
            new_setting = AppSetting(key=prefix, value=1)
            db.session.add(new_setting)
            return 1

    @staticmethod
    def get_obj(id) -> Operations:
        ws = db.session.query(Operations).get(id)
        if not ws:
            raise NotFoundError("Estacion de trabajo no ecnontrada")
        return ws

    @staticmethod
    def get_obj_list(filters: None) -> list[Operations]:

        op = apply_filters(Operations, filters, True)
        op = op.all()

        return op

    @staticmethod
    def patch_obj(obj: Operations, data: dict) -> Operations:
        dto = OperationPatchDTO(**data)
        if dto.code:
            obj.code = dto.code
        if dto.name:
            obj.name = dto.name
        if dto.rate_hour:
            obj.rate_hour = dto.rate_hour
        if dto.mission:
            obj.mission = dto.mission
        if dto.kpi:
            obj.kpi = dto.kpi
        if dto.responsible:
            obj.responsible = dto.responsible
        if (
            dto.code is None
            and dto.name is None
            and dto.rate_hour is None
            and dto.mission is None
            and dto.kpi is None
        ):
            raise ValueError("No se proporsiono un campo valido")

        try:
            db.session.commit()
            return obj
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def soft_delete(obj: Operations, data: dict) -> Operations:
        dto = OperationStatusDTO(**data)
        obj.is_active = dto.is_active
        try:
            db.session.commit()
            return obj
        except Exception:
            db.session.rollback()
            current_app.logger.warning("Error al cambiar el estado de Operation")
            raise

    @staticmethod
    def delete_obj(obj: Operations) -> bool:
        try:
            db.session.delete(obj)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise


class ProductionResourceService:

    @staticmethod
    def get_obj(id: int) -> ProductionResource:
        pr = ProductionResource.query.get(id)
        if not pr:
            raise NotFoundError(f"No existe el Recurso(id:{id})")
        return pr

    @staticmethod
    def get_obj_list(filters=None) -> list[ProductionResource]:
        query = apply_filters(
            model=ProductionResource, filters=filters, query_only=True
        )
        q = query.all()
        return q

    @staticmethod
    def create_obj(data):
        with db.session.begin():
            dto = ProductionResourceDTO(**data)
            new_obj = ProductionResourceService.create_production_resource(
                name=dto.name,
                description=dto.description,
                kind=dto.kind,
                operation_id=dto.operation_id,
                qty=dto.qty,
                efficiency=dto.efficiency,
                setup_min=dto.setup_min,
            )

            return new_obj

    @staticmethod
    def create_production_resource(
        name,
        qty,
        kind,
        operation_id=None,
        description=None,
        efficiency=None,
        setup_min=None,
    ) -> ProductionResource:

        from ..common.services import SecuenceGenerator

        sec = SecuenceGenerator.get_next_number("production_resource_sec")
        code = f"R{sec:04d}"

        print("production resource code", code)

        pr = ProductionResource(
            name=name,
            code=code,
            qty=qty,
            kind=kind,
            operation_id=operation_id,
            description=description,
            efficiency=efficiency,
            setup_min=setup_min,
        )
        db.session.add(pr)
        print("resource", pr)
        return pr

    @staticmethod
    def patch_obj(obj: ProductionResource, data: dict):

        dto = ProductionResourcePatchDTO(**data)

        print(dto)
        if dto.name:
            obj.name = dto.name

        if dto.qty:
            obj.qty = dto.qty

        if dto.description:
            obj.description = dto.description

        if dto.efficiency:
            obj.efficiency = dto.efficiency

        if dto.is_active is not None:
            obj.is_active = dto.is_active

        if dto.setup_min:
            obj.setup_min = dto.setup_min

        try:
            db.session.commit()
            return obj
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_obj(obj: ProductionResource) -> bool:
        try:
            db.session.delete(obj)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False


class VariantResourceUsageService:

    @staticmethod
    def create_obj(data: dict):
        from .dto_production_resources import VariantResourceUsageDTO

        with db.session.begin():
            dto = VariantResourceUsageDTO(**data)
            new_reg = VariantResourceUsageService.upsert_variant_resource_usage(
                variant_ids=dto.variant_ids,
                resource_id=dto.resource_id,
                operation_id=dto.operation_id,
                std_min_unit=dto.std_min_unit,
            )
            return new_reg

    @staticmethod
    def create_variant_resource_usage(
        variant_ids: list[int],
        resource_id: int,
        operation_id: int,
        std_min_unit: Decimal,
    ):
        reg = []
        for v in variant_ids:

            new_reg = VariantOperationResource(
                variant_id=v,
                resource_id=resource_id,
                operation_id=operation_id,
                std_min_unit=std_min_unit,
            )
            db.session.add(new_reg)
            reg.append(new_reg)
        return reg

    @staticmethod
    def upsert_variant_resource_usage(
        variant_ids: list[int], resource_id: int, operation_id: int, std_min_unit
    ) -> dict:
        """
        Crea o actualiza el tiempo estándar (min/unid) para
        (operation_id, resource_id) aplicado a múltiples variantes.
        """

        # Existencia de entidades
        if not ProductionResource.query.get(resource_id):
            raise NotFoundError(f"Recurso {resource_id} no existe")
        if not Operations.query.get(operation_id):
            raise NotFoundError(f"Operación {operation_id} no existe")

        # (Opcional) Verifica que las variantes existan
        from ..products.models import ProductVariant

        existing_variants = {
            v.id
            for v in ProductVariant.query.with_entities(ProductVariant.id)
            .filter(ProductVariant.id.in_(variant_ids))
            .all()
        }
        missing = set(variant_ids) - existing_variants
        if missing:
            raise NotFoundError(f"Variantes inexistentes: {sorted(missing)}")

        # Trae registros existentes para este (op, res) y ese set de variantes
        existing_rows = VariantOperationResource.query.filter(
            VariantOperationResource.resource_id == resource_id,
            VariantOperationResource.operation_id == operation_id,
            VariantOperationResource.variant_id.in_(variant_ids),
        ).all()

        by_variant = {row.variant_id: row for row in existing_rows}

        created, updated = [], []

        for vid in variant_ids:
            row = by_variant.get(vid)
            if row is None:
                row = VariantOperationResource(
                    variant_id=vid,
                    resource_id=resource_id,
                    operation_id=operation_id,
                    std_min_unit=std_min_unit,
                )
                db.session.add(row)
                created.append(vid)
            else:
                # Actualiza sólo si cambia (evita flush sucio)
                if row.std_min_unit != std_min_unit:
                    row.std_min_unit = std_min_unit
                    updated.append(vid)

        # Deja IDs listos sin cerrar transacción
        db.session.flush()

        return {
            "created_variant_ids": created,
            "updated_variant_ids": updated,
            "count_created": len(created),
            "count_updated": len(updated),
            "operation_id": operation_id,
            "resource_id": resource_id,
            "std_min_unit": str(std_min_unit),
        }

    @staticmethod
    def get_obj(id: int):
        obj = VariantOperationResource.query.get(id)
        if obj is None:
            return NotFoundError("Registro no encontrado")
        return obj

    @staticmethod
    def get_obj_list(filters: dict = None):
        query = apply_filters(
            model=VariantOperationResource, filters=filters, query_only=True
        )
        return query.all()

    @staticmethod
    def patch_obj(obj: VariantOperationResource, std_time):
        from .dto_production_resources import VariantResourceUsagePatchDTO

        dto = VariantResourceUsagePatchDTO(**std_time)
        obj.std_min_unit = dto
        try:
            db.session.commit()
            return obj
        except Exception:
            raise
