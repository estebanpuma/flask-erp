from enum import Enum


class OrderStatus(str, Enum):
    DRAFT = "Borrador"
    PENDING = "Pendiente"
    APPROVED = "Aprobada"
    PLANNED = "Planificada"
    CANCELED = "Cancelada"
    DELIVERED = "Entregada"
    REJECTED = "Rechazada"
    WIP = "En proceso"

    @classmethod
    def has_value(cls, value):
        return value in [member.value for member in cls]


class SizeCategory(str, Enum):
    MAN = "Hombre"
    WOMAN = "Mujer"
    KID = "Infantil"

    @classmethod
    def has_value(cls, value):
        return value in [member.value for member in cls]


class PaymentStatus(str, Enum):
    UNPAID = "Sin pago"
    PARTIAL = "Parcialmente pagada"
    PAID = "Pagada"

    @classmethod
    def has_value(cls, value):
        return value in [member.value for member in cls]


class ProductLotStatusEnum(str, Enum):
    """
    Estado de lotes de productos
    """

    IN_STOCK = "En stock"
    DELIVERED = "Entregado"
    REJECTED = "Rechazado"
    # RETURNED = 'Regresado'

    @classmethod
    def has_value(cls, value):
        return value in [member.value for member in cls]


class InventoryMovementType(
    str, Enum
):  # actualizar en inventory movement DTO si existe algun cambio
    """
    Tipos de movimiento de inventario <materia prima> (Actializar en DTOs si existen cambios)
    """

    IN = "Ingreso"
    OUT = "Egreso"
    ADJUST = "Ajuste"
    TRANSFER = "Transferencia"

    @classmethod
    def has_value(cls, value):
        return value in [member.value for member in cls]


class ProductMovementTypeEnum(str, Enum):
    """
    Tipos de movimientos de lote de producto
    """

    IN = "Ingreso"
    DELIVERY = "Entrega"
    RETURN = "Devolucion"
    REPROCESS = "Reproceso"
    ADJUST = "Ajuste"
    TRANSFER = "Transferencia"

    @classmethod
    def has_value(cls, value):
        return value in [member.value for member in cls]


# Cual fue la razon que origino ese lote de productos
class ProductionSourceTypeEnum(str, Enum):
    """
    Origenes/Triggers de produccion/productos
    """

    SALES = "Ventas"
    STOCK = "Stock"
    RDI = "Desarrollo e innovación"

    @classmethod
    def has_value(cls, value):
        return value in [member.value for member in cls]
