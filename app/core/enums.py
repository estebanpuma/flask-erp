from enum import Enum

class OrderStatus(Enum):
    DRAFT = 'Borrador'
    APPROVED = 'Aprobada'
    CANCELED = 'Cancelada'
    DELIVERED = 'Entregada'
    WIP = "En proceso"


class SizeCategory(Enum):
    MAN = 'Hombre'
    WOMAN = 'Mujer'
    KID = 'Infantil'


class PaymentStatus(Enum):
    UNPAID = 'Sin pago'
    PARTIAL = 'Parcialmente pagada'
    PAID = 'Pagada'