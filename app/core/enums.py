from enum import Enum

class OrderStatus(Enum):
    DRAFT = 'Borrador'
    APPROVED = 'Aprobada'
    CANCELLED = 'Cancelada'
    DELIVERED = 'Entregada'
    WIP = "En proceso"