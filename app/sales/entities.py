from ..core.exceptions import AppError
from ..core.enums import PaymentStatus

class SalesOrderEntity:
    """
    Encapsula la lógica de negocio y cálculos de la orden.
    Recibe modelos (no DTOs, no datos crudos).
    """

    def __init__(self, order):
        self.order = order

    def calculate_subtotal(self):
        """
        Calcula el subtotal sumando los subtotales de las líneas.
        """
        return sum(line.subtotal for line in self.order.lines)

    def calculate_total(self):
        """
        Calcula el total considerando descuento global y tax.
        """
        subtotal = self.calculate_subtotal()
        discount = self.order.discount or 0.0
        tax = self.order.tax or 0.0
        return round(subtotal - discount + tax, 2)


    def add_payment(self, amount: float):
        """Registra un pago a la orden de venta"""
        if amount > self.order.amount_due:
            raise AppError("El pago excede el saldo pendiente de la orden.")

        self.order.amount_paid += amount
        self.order.amount_due -= amount
        self.update_payment_status()

    def remove_payment(self, amount: float):
        """Elimina un pago de la orden de venta"""
        self.order.amount_paid -= amount
        self.order.amount_due += amount
        self.update_payment_status()

    def update_payment_status(self):
        """Actualiza el estado de pago de un pedido"""
        print(f'En update entity: {self.order.amount_paid}')
        if self.order.amount_due == 0:
            self.order.payment_status = PaymentStatus.PAID.value
        elif self.order.amount_paid > 0:
            self.order.payment_status = PaymentStatus.PARTIAL.value
        else:
            self.order.payment_status = PaymentStatus.UNPAID.value
