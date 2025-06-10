# services/material_lot_service.py
from app import db
from .models import MaterialLot, Material, InventoryMovement
from ..suppliers.models import Supplier
from ..inventory.models import Warehouse
from .dto.material_lot_dto import MaterialLotCreateDTO, MaterialLotUpdateDTO
from ..core.exceptions import NotFoundError, ValidationError
from datetime import date
from ..core.filters import apply_filters
from .material_services import MaterialStock, MaterialStockService
from sqlalchemy.orm import joinedload # Importa joinedload

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
            received_date=dto.received_date or date.today(),
            note=dto.note
        )
        db.session.add(lot)

        # Crear automáticamente el movimiento de entrada (IN)
        movement = InventoryMovement(
            movement_type='IN',
            lot=lot,
            quantity=dto.quantity,
            origin_warehouse_id=None,
            destination_warehouse_id=lot.warehouse_id,
            date=lot.received_date,
            note='Ingreso inicial al crear lote'
        )
        db.session.add(movement)

        MaterialStockService.update_stock(lot.material_id, lot.warehouse_id)

        return lot

    @staticmethod
    def get_obj(lot_id: int) -> MaterialLot:
        lot = db.session.query(MaterialLot).options(
            joinedload(MaterialLot.material) # Carga anticipadamente la relación 'material'
        ).get(lot_id) # Usamos .get() al final para buscar por PK
        if not lot:
            raise NotFoundError(f"Lote con id {lot_id} no encontrado.")
        return lot

    @staticmethod
    def get_obj_list(filters: dict = None):
        return apply_filters(MaterialLot, filters)
    
    
    @staticmethod
    def get_lots_by_material(material_id:int, filters=None)->list[MaterialLot]:
        """
        Obtiene una lista de lotes de material filtrados.

        Args:
            material_id (int): El ID del material para el que se buscan los lotes.
            filters (dict, optional): Un diccionario de filtros adicionales.
                                      Ej: {'gt_quantity': 0} para cantidad > 0.
                                      Los nombres de los filtros aquí son claves para tu lógica.

        Returns:
            list[MaterialLot]: Una lista de objetos MaterialLot que cumplen con los criterios.
        """
        # 1. Inicia la consulta base
        # Siempre filtramos por material_id
        query = MaterialLot.query.options(db.joinedload(MaterialLot.material)).filter(MaterialLot.material_id == material_id)
        # 2. Aplica filtros adicionales si se proporcionan
        print(f'Adentro {query}')
        if filters:
            # Filtro para cantidad mayor que (gt = greater than)
            if 'quantity__gt' in filters: # Usamos un nombre más explícito para la clave del filtro
                query = query.filter(MaterialLot.quantity > filters['quantity__gt'])
        
        # 3. Ejecuta la consulta y devuelve los resultados
        # .all() ejecuta la consulta y trae todos los resultados
        lots = query.all()
        return lots

    @staticmethod
    def patch_obj(lot: MaterialLot, dto: MaterialLotUpdateDTO) -> MaterialLot:
        

        if dto.unit_cost is not None:
            lot.unit_cost = dto.unit_cost

        if dto.received_date is not None:
            lot.received_date = dto.received_date

        if dto.lot_number is not None:
            lot.lot_number = dto.lot_number

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
        
        from .material_services import MaterialStockService

        MaterialStockService.update_stock(lot.material_id, lot.warehouse_id)

        try:
            db.session.delete(lot)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise
