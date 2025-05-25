from enum import Enum

class OrderStatus(Enum):
    DRAFT = 'Borrador'
    PENDING = 'Pendiente'
    APPROVED = 'Aprobada'
    CANCELED = 'Cancelada'
    DELIVERED = 'Entregada'
    WIP = "En proceso"


class SizeCategory(Enum):
    MAN = 'Hombre'
    WOMAN = 'Mujer'
    KID = 'Infantil'