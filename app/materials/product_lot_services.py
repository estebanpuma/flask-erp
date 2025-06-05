# services/product_lot_service.py
from app import db
from .models import ProductLot, ProductStock, ProductLotMovement
from ..production.models import ProductionOrder
from ..products.models import ProductVariant
from ..inventory.models import Warehouse
from .product_stock_services import ProductStockService
from .dto.product_lot_dto import ProductLotCreateDTO, ProductLotUpdateDTO
from .dto.product_lot_movement_dto import ProductLotAdjustmentDTO, ProductLotMovementOutDTO, ProductMovementTransferDTO
from ..core.exceptions import NotFoundError, ValidationError
from ..core.filters import apply_filters
from ..core.enums import ProductLotStatusEnum, ProductMovementTypeEnum
from datetime import datetime


class ProductLotService:

    @staticmethod
    def create_obj(data:dict):
        with db.session.begin():
            dto = ProductLotCreateDTO(**data)
            product_lot = ProductLotService.create(dto)
            return product_lot

    @staticmethod
    def create(dto: ProductLotCreateDTO) -> ProductLot:
        # Validar existencia de entidades relacionadas
        product_variant = db.session.get(ProductVariant, dto.product_variant_id)
        if not product_variant:
            raise NotFoundError(f"ProductVariant con id {dto.product_variant_id} no encontrado.")

        warehouse = db.session.get(Warehouse, dto.warehouse_id)
        if not warehouse:
            raise NotFoundError(f"Warehouse con id {dto.warehouse_id} no encontrado.")

        #production_order = db.session.get(ProductionOrder, dto.production_order_id)
        #if not production_order:
        #    raise NotFoundError(f"ProductionOrder con id {dto.production_order_id} no encontrado.")

        lot = ProductLot(
            lot_number=dto.lot_number.strip(),
            product_variant_id=dto.product_variant_id,
            warehouse_id=dto.warehouse_id,
            quantity=dto.quantity,
            unit_cost=dto.unit_cost,
            production_order_id=dto.production_order_id,
            received_date=dto.received_date or datetime.today(),
            status=ProductLotStatusEnum.IN_STOCK.value  # Estado inicial
        )
        db.session.add(lot)

        # Registrar movimiento inicial
        movement = ProductLotMovement(
            product_lot_id=lot.id,
            quantity=dto.quantity,
            movement_type=ProductMovementTypeEnum.IN.value,
            origin_warehouse_id=None,
            destination_warehouse_id=dto.warehouse_id,
            note=f'Ingreso inicial',
            date=datetime.today()
        )
        db.session.add(movement)

        # Actualizar stock consolidado
        ProductStockService.update_stock(dto.product_variant_id, dto.warehouse_id)

        return lot

    @staticmethod
    def get_obj(lot_id: int) -> ProductLot:
        lot = db.session.get(ProductLot, lot_id)
        if not lot:
            raise NotFoundError(f"ProductLot con id {lot_id} no encontrado.")
        return lot

    @staticmethod
    def get_obj_list(filters: dict = None):
        
        return apply_filters(ProductLot, filters)

    @staticmethod
    def patch_obj(lot:ProductLot, data:dict) -> ProductLot:
        dto = ProductLotUpdateDTO(**data)
        if dto.quantity is not None:
            if dto.quantity < 0:
                raise ValidationError("La cantidad no puede ser negativa.")
            lot.quantity = dto.quantity

        if dto.unit_cost is not None:
            lot.unit_cost = dto.unit_cost

        # Actualizar stock consolidado
        ProductStockService.update_stock(lot.product_variant_id, lot.warehouse_id)
        try:
            db.session.commit()
            return 
        except Exception as e:
            db.session.rollback()
            raise 
    
    @staticmethod
    def adjust_obj(data:dict):
        with db.session.begin():
            dto = ProductLotAdjustmentDTO(**data)
            lot = ProductLotService.adjust_to_real(dto.new_quantity, dto.product_lot_id, dto.note)
            return lot

    @staticmethod
    def adjust_to_real(new_quantity:int, product_lot_id:int, note:str=None) -> ProductLot:
        lot = ProductLotService.get_obj(product_lot_id)

        adjustment = new_quantity - lot.quantity
        if adjustment == 0:
            raise ValidationError("La cantidad real es igual a la registrada. No hay ajuste que hacer.")
        if new_quantity < 0:
            raise ValidationError("La cantidad real no puede ser negativa.")

        #obtener a diferencia
        old_quantity = lot.quantity
        difference = new_quantity - old_quantity

        # Actualizar la cantidad real
        lot.quantity = new_quantity

        # Crear movimiento de ajuste
        from .models import ProductLotMovement  # Evitamos dependencias cíclicas
        movement = ProductLotMovement(
            product_lot_id=lot.id,
            movement_type=ProductMovementTypeEnum.ADJUST.value,
            quantity=adjustment,
            origin_warehouse_id=lot.warehouse_id,
            #destination_warehoue_id = lot.warehouse_id,
            note= note or f"Ajuste real de inventario (ajuste: {difference})",
            date=datetime.today()
        )
        db.session.add(movement)


        # Actualizar stock consolidado
        ProductStockService.update_stock(lot.product_variant_id, lot.warehouse_id)

        return lot

    @staticmethod
    def delete_obj(lot:ProductLot):

        # Validar que no esté comprometido o con movimientos (¡opcional!)
        if lot.movements.count() > 0:
            raise ValidationError("No se puede eliminar un lote con movimientos registrados.")
        if lot.status != 'in_stock':
            raise ValidationError("No se puede eliminar un lote que ya no está en stock.")

        try: 
            db.session.delete(lot)

            # Actualizar stock consolidado
            ProductStockService.update_stock(lot.product_variant_id, lot.warehouse_id)
            db.session.commit()
            return True
        except Exception as e:

            db.session.rollback()
            raise

# services/product_lot_movement_service.py
class ProductLotMovementService:

    @staticmethod
    def create_out_obj(data:dict)->ProductLotMovement:
        with db.session.begin():
            dto = ProductLotMovementOutDTO(**data)
            movement = ProductLotMovementService.create_out(dto.product_lot_id, 
                                                        dto.quantity,
                                                        dto.note)
            return movement

    @staticmethod
    def create_out(product_lot_id:int, 
                    quantity:int, 
                    note:str = None ) -> ProductLotMovement:
        
        lot = db.session.get(ProductLot, product_lot_id)
        if not lot:
            raise NotFoundError(f"ProductLot con id {product_lot_id} no encontrado.")

        # Validar cantidad positiva
        if quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")

        
        if quantity > lot.quantity:
            raise ValidationError(
                f"No hay suficiente stock disponible en el lote (disponible: {lot.quantity}).")
        lot.quantity -= quantity
        
        # Crear el movimiento para la trazabilidad
        movement = ProductLotMovement(
            product_lot_id=lot.id,
            movement_type=ProductMovementTypeEnum.DELIVERY.value,
            quantity=quantity,
            note=note,
            date=datetime.today(),
            origin_warehouse_id= lot.warehouse_id,
           
        )
        db.session.add(movement)

        # Actualizar stock consolidado
        ProductStockService.update_stock(lot.product_variant_id, lot.warehouse_id)

        return movement
    

    @staticmethod
    def create_transfer_obj(data):
        with db.session.begin():
            dto = ProductMovementTransferDTO(**data)
            transfer = ProductLotMovementService.create_transfer(dto.product_lot_id,
                                                                 dto.destination_warehouse_id,
                                                                 dto.note)
            return transfer

    @staticmethod
    def create_transfer(product_lot_id:int, 
                    destination_warehouse_id:int,
                    note:str = None ) -> ProductLotMovement:
        
        lot = db.session.get(ProductLot, product_lot_id)
        if not lot:
            raise NotFoundError(f"ProductLot con id {product_lot_id} no encontrado.")
        
        from ..inventory.models import Warehouse
        destination_warehouse = Warehouse.query.get(destination_warehouse_id)

        if not destination_warehouse:
            raise ValidationError(f'Bodega co id:{destination_warehouse_id} no encontrada')

        # Validar cantidad positiva
        if lot.quantity <= 0:
            raise ValidationError("La cantidad del lote a transferir debe ser mayor a cero.")

        
        old_warehouse_id = lot.warehouse_id

        # Crear el movimiento para la trazabilidad
        movement = ProductLotMovement(
            product_lot_id=lot.id,
            movement_type=ProductMovementTypeEnum.TRANSFER.value,
            quantity=lot.quantity,
            note=note,
            date=datetime.today(),
            origin_warehouse_id= lot.warehouse_id,
            destination_warehouse_id = destination_warehouse_id
           
        )

        #actualizar el id de la bodega
        lot.warehouse_id = destination_warehouse_id
        db.session.add(movement)

        # Actualizar stock consolidado en la badega anteriro y la nueva
        ProductStockService.update_stock(lot.product_variant_id, old_warehouse_id)
        ProductStockService.update_stock(lot.product_variant_id, lot.warehouse_id)

        return movement


    @staticmethod
    def get_obj(movement_id: int) -> ProductLotMovement:
        movement = db.session.get(ProductLotMovement, movement_id)
        if not movement:
            raise NotFoundError(f"ProductLotMovement con id {movement_id} no encontrado.")
        return movement

    @staticmethod
    def get_obj_list(filters: dict = None):
        return apply_filters(ProductLotMovement, filters)
