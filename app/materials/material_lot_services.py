# services/material_lot_service.py
from app import db
from .models import MaterialLot, Material, InventoryMovement
from ..suppliers.models import Supplier
from ..inventory.models import Warehouse
from .dto.material_lot_dto import MaterialLotCreateDTO, MaterialLotUpdateDTO
from ..core.exceptions import NotFoundError, ValidationError
from datetime import date
from ..core.filters import apply_filters

class MaterialLotService:

    @staticmethod
    def create_obj(data:dict):
        with db.session.begin():
            dto = MaterialLotCreateDTO(**data)
            lot = MaterialLotService.create(dto)
            return lot

    @staticmethod
    def create(dto: MaterialLotCreateDTO) -> MaterialLot:
        # Validar que material, proveedor y bodega existan
        material = db.session.get(Material, dto.material_id)
        if not material:
            raise NotFoundError(f"Material con id {dto.material_id} no encontrado.")

        supplier = db.session.get(Supplier, dto.supplier_id)
        if not supplier:
            raise NotFoundError(f"Proveedor con id {dto.supplier_id} no encontrado.")

        warehouse = db.session.get(Warehouse, dto.warehouse_id)
        if not warehouse:
            raise NotFoundError(f"Bodega con id {dto.warehouse_id} no encontrada.")

        lot = MaterialLot(
            lot_number=dto.lot_number.strip(),
            material_id=dto.material_id,
            supplier_id=dto.supplier_id,
            warehouse_id=dto.warehouse_id,
            quantity=dto.quantity,
            unit_cost=dto.unit_cost,
            received_date=dto.received_date or date.today()
        )
        db.session.add(lot)

        # Crear automáticamente el movimiento de entrada (IN)
        movement = InventoryMovement(
            movement_type='IN',
            lot=lot,
            quantity=dto.quantity,
            date=lot.received_date,
            note='Ingreso inicial al crear lote'
        )
        db.session.add(movement)

        return lot

    @staticmethod
    def get_obj(lot_id: int) -> MaterialLot:
        lot = db.session.get(MaterialLot, lot_id)
        if not lot:
            raise NotFoundError(f"Lote con id {lot_id} no encontrado.")
        return lot

    @staticmethod
    def get_obj_list(filters: dict = None):
        return apply_filters(MaterialLot, filters)

    @staticmethod
    def patch_obj(lot: MaterialLot, dto: MaterialLotUpdateDTO) -> MaterialLot:
        

        # Solo campos permitidos
        if dto.quantity is not None:
            if dto.quantity < lot.quantity_committed:
                raise ValidationError(
                    f"No se puede establecer la cantidad menor a la ya comprometida ({lot.quantity_committed}).")
            lot.quantity = dto.quantity

        if dto.unit_cost is not None:
            lot.unit_cost = dto.unit_cost

        if dto.warehouse_id is not None:
            warehouse = db.session.get(Warehouse, dto.warehouse_id)
            if not warehouse:
                raise NotFoundError(f"Bodega con id {dto.warehouse_id} no encontrada.")
            lot.warehouse_id = dto.warehouse_id
        try:
            db.session.commit()
            return lot
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def delete_obj(lot: MaterialLot):
        
        # Validar que no haya movimientos ya registrados con este lote
        if lot.movements.count() > 0:
            raise ValidationError("No se puede eliminar un lote con movimientos registrados (trazabilidad).")

        # Validar que no esté comprometido en producción
        if lot.quantity_committed > 0:
            raise ValidationError("No se puede eliminar un lote comprometido en producción.")

        try:
            db.session.delete(lot)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise
