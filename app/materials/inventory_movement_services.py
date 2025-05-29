# services/inventory_movement_service.py
from app import db
from .models import InventoryMovement, MaterialLot
from .dto.inventory_movements_dto import InventoryMovementCreateDTO, InventoryAdjustmentDTO
from ..core.exceptions import NotFoundError, ValidationError
from ..core.filters import apply_filters
from datetime import datetime


class InventoryMovementService:

    @staticmethod
    def create_obj(data:dict):
        with db.session.begin():
            dto = InventoryMovementCreateDTO(**data)
            movement = InventoryMovementService.create(dto)
            return movement

    @staticmethod
    def create(dto: InventoryMovementCreateDTO) -> InventoryMovement:
        lot = db.session.get(MaterialLot, dto.lot_id)
        if not lot:
            raise NotFoundError(f"Lote con id {dto.lot_id} no encontrado.")

        # Validar tipo de movimiento
        movement_type = dto.movement_type

        if movement_type == 'IN':
            # Entrada ➜ sumamos la cantidad
            lot.quantity += dto.quantity
        elif movement_type == 'OUT':
            # Salida ➜ validamos stock disponible
            available_quantity = lot.quantity - lot.quantity_committed
            if dto.quantity > available_quantity:
                raise ValidationError(
                    f"No hay suficiente stock disponible en el lote (disponible: {available_quantity}).")
            lot.quantity -= dto.quantity
        else:
            raise ValidationError(f"Tipo de movimiento no permitido: {movement_type}")

        # Registrar el movimiento
        movement = InventoryMovement(
            movement_type=movement_type,
            lot_id=dto.lot_id,
            quantity=dto.quantity,
            note=dto.note,
            date=datetime.utcnow()
        )
        db.session.add(movement)

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
            if 'movement_type' in filters:
                query = query.filter(InventoryMovement.movement_type == filters['movement_type'])
                return query.order_by(InventoryMovement.date.desc()).all()
            if 'material_id' in filters:
                query = query.filter(MaterialLot.material_id == filters['material_id'])
                return query.order_by(InventoryMovement.date.desc()).all()
            if 'warehouse_id' in filters:
                query = query.filter(MaterialLot.warehouse_id == filters['warehouse_id'])
                return query.order_by(InventoryMovement.date.desc()).all()
            else:
                return apply_filters(InventoryMovementService, filters)
        return InventoryMovement.query.all()
        

    @staticmethod
    def adjust_obj(data:dict):
        with db.session.begin():
            dto = InventoryAdjustmentDTO(**data)
            adjusment = InventoryMovementService.adjust_to_real(dto)
            return adjusment

    def adjust_to_real(dto: InventoryAdjustmentDTO) -> InventoryMovement:
        lot = db.session.get(MaterialLot, dto.lot_id)
        if not lot:
            raise NotFoundError(f"Lote con id {dto.lot_id} no encontrado.")

        adjustment = dto.new_quantity - lot.quantity
        if adjustment == 0:
            raise ValidationError("La cantidad real ingresada es igual a la registrada. No hay ajuste que realizar.")

        # Validamos que no quede en negativo (no debería, ya que new_quantity >= 0)
        if dto.new_quantity < 0:
            raise ValidationError("La cantidad real no puede ser negativa.")

        # Actualizamos el stock del lote
        lot.quantity = dto.new_quantity

        # Registramos el movimiento
        movement = InventoryMovement(
            movement_type='ADJUST',
            lot_id=lot.id,
            quantity=adjustment,  # Positivo o negativo
            note=dto.note,
            date=datetime.today()
        )
        db.session.add(movement)

        return movement