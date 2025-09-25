# services/inventory_movement_service.py
from datetime import datetime

from app import db

from ..core.exceptions import NotFoundError, ValidationError
from ..core.filters import apply_filters
from .dto.inventory_movements_dto import (
    InventoryMovementAdjustDTO,
    InventoryMovementOutDTO,
    InventoryMovementTransferDTO,
)
from .material_services import MaterialStockService
from .models import InventoryMovement, MaterialLot


class InventoryMovementService:

    @staticmethod
    def create_obj_out(data: dict):
        with db.session.begin():
            dto = InventoryMovementOutDTO(**data)
            movement = InventoryMovementService.create_out(
                dto.lot_id, dto.quantity, dto.note
            )
            return movement

    @staticmethod
    def create_obj_transfer(data: dict):
        with db.session.begin():
            dto = InventoryMovementTransferDTO(**data)
            movement = InventoryMovementService.transfer_material_lot(
                lot_id=dto.lot_id,
                destination_warehouse_id=dto.destination_warehouse_id,
                note=dto.note,
            )
            return movement

    @staticmethod
    def adjust_obj(data: dict) -> InventoryMovement:
        with db.session.begin():
            dto = InventoryMovementAdjustDTO(**data)
            adjusment = InventoryMovementService.adjust_to_real(
                lot_id=dto.lot_id, real_quantity=dto.quantity, note=dto.note
            )
            return adjusment

    @staticmethod
    def create_out(lot_id: int, quantity: float, note: str = None) -> InventoryMovement:
        lot = db.session.get(MaterialLot, lot_id)
        if not lot:
            raise NotFoundError(f"MaterialLot con id {lot_id} no encontrado.")

        available_quantity = lot.quantity - lot.quantity_committed
        if quantity > available_quantity:
            raise ValidationError(
                f"No hay suficiente stock disponible en el lote (disponible: {available_quantity})."
            )

        # Descontar la cantidad
        lot.quantity -= quantity

        # Crear movimiento de salida
        movement = InventoryMovement(
            movement_type="OUT",
            lot_id=lot.id,
            quantity=quantity,
            origin_warehouse_id=lot.warehouse_id,
            destination_warehouse_id=None,
            note=note or "Salida de materia prima",
            date=datetime.today(),
        )
        db.session.add(movement)

        # Actualizar stock consolidado
        MaterialStockService.update_stock(lot.material_id, lot.warehouse_id)

        return movement

    @staticmethod
    def transfer_material_lot(
        lot_id: int, destination_warehouse_id: int, note: str = None
    ) -> InventoryMovement:
        lot = db.session.get(MaterialLot, lot_id)
        if not lot:
            raise NotFoundError(f"MaterialLot con id {lot_id} no encontrado.")

        if lot.warehouse_id == destination_warehouse_id:
            raise ValidationError(
                "La bodega de destino debe ser diferente a la de origen."
            )

        # temporalmente bloqueamos movimientos de maeriales reservados, luego se pueden crear particiones de lotes
        if lot.quantity_committed > 0:
            raise ValidationError(
                "No se puede transferir un lote con reservas comprometidas."
            )

        old_warehouse_id = lot.warehouse_id

        # Actualiza la ubicación real del lote
        lot.warehouse_id = destination_warehouse_id

        # Crear el movimiento de transferencia
        movement = InventoryMovement(
            movement_type="TRANSFER",
            lot_id=lot.id,
            quantity=lot.quantity,
            origin_warehouse_id=old_warehouse_id,
            destination_warehouse_id=destination_warehouse_id,
            note=note
            or f"Transferencia de bodega {old_warehouse_id} a {destination_warehouse_id}",
            date=datetime.today(),
        )
        db.session.add(movement)

        # Actualiza stock consolidado en ambas bodegas
        MaterialStockService.update_stock(lot.material_id, old_warehouse_id)
        MaterialStockService.update_stock(lot.material_id, destination_warehouse_id)

        return movement

    @staticmethod
    def adjust_to_real(
        lot_id: int, real_quantity: float, note: str = None
    ) -> InventoryMovement:
        lot = db.session.get(MaterialLot, lot_id)
        if not lot:
            raise NotFoundError(f"MaterialLot con id {lot_id} no encontrado.")

        if real_quantity < 0:
            raise ValidationError("La cantidad real debe ser igual o mayor a cero.")

        old_quantity = lot.quantity
        difference = real_quantity - old_quantity

        # Ajustar la cantidad real
        lot.quantity = real_quantity

        # Crear movimiento de ajuste
        movement = InventoryMovement(
            movement_type="ADJUST",
            lot_id=lot.id,
            quantity=difference,  # La cantidad final real
            origin_warehouse_id=lot.warehouse_id,
            destination_warehouse_id=None,
            note=str(note) + f"Ajuste real de inventario (diferencia: {difference})",
            date=datetime.today(),
            # Opcional: podrías agregar un campo adjustment_amount = difference
        )
        db.session.add(movement)

        # Actualizar stock consolidado
        MaterialStockService.update_stock(lot.material_id, lot.warehouse_id)

        return movement

    @staticmethod
    def get_obj(movement_id: int) -> InventoryMovement:
        movement = db.session.get(InventoryMovement, movement_id)
        if not movement:
            raise NotFoundError(f"Movimiento con id {movement_id} no encontrado.")
        return movement

    @staticmethod
    def get_obj_list(filters: dict = None):
        query = db.session.query(InventoryMovement).join(MaterialLot)
        if filters:
            if "movement_type" in filters:
                query = query.filter(
                    InventoryMovement.movement_type == filters["movement_type"]
                )
                return query.order_by(InventoryMovement.date.desc()).all()
            if "material_id" in filters:
                query = query.filter(MaterialLot.material_id == filters["material_id"])
                return query.order_by(InventoryMovement.date.desc()).all()
            if "warehouse_id" in filters:
                query = query.filter(
                    MaterialLot.warehouse_id == filters["warehouse_id"]
                )
                return query.order_by(InventoryMovement.date.desc()).all()
            else:
                return apply_filters(InventoryMovementService, filters)
        return InventoryMovement.query.all()
