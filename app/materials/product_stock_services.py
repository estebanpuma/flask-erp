from app import db

from ..core.enums import ProductLotStatusEnum
from ..core.filters import apply_filters
from .models import ProductLot, ProductStock


class ProductStockService:

    @staticmethod
    def get_obj_list(filters=None):
        query = db.session.query(ProductStock)
        if filters:
            if "product_variant_id" in filters:
                query = query.filter(
                    ProductStock.product_variant_id == filters["product_variant_id"]
                )
                return query.all()
            if "warehouse_id" in filters:
                query = query.filter(
                    ProductStock.warehouse_id == filters["warehouse_id"]
                )
                return query.all()

        return apply_filters(ProductStock, filters)

    @staticmethod
    def update_stock(product_variant_id: int, warehouse_id: int):
        # Calcular el stock consolidado sumando los ProductLot con status 'in_stock'
        stock_sum = (
            db.session.query(db.func.sum(ProductLot.quantity))
            .filter_by(
                product_variant_id=product_variant_id,
                warehouse_id=warehouse_id,
                status=ProductLotStatusEnum.IN_STOCK.value,
            )
            .scalar()
        ) or 0.0

        # Buscar si ya existe el registro
        product_stock = (
            db.session.query(ProductStock)
            .filter_by(product_variant_id=product_variant_id, warehouse_id=warehouse_id)
            .first()
        )

        if not product_stock:
            product_stock = ProductStock(
                product_variant_id=product_variant_id,
                warehouse_id=warehouse_id,
                quantity=stock_sum,
            )
            db.session.add(product_stock)
        else:
            product_stock.quantity = stock_sum
