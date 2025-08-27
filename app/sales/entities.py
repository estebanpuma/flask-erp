from ..core.exceptions import AppError
from ..core.enums import PaymentStatus
from decimal import Decimal
from decimal import getcontext, ROUND_HALF_UP

getcontext().rounding = ROUND_HALF_UP
CENT = Decimal('0.01')

class SalesOrderEntity:
    """
    Encapsula la lógica de negocio y cálculos de la orden.
    Recibe modelos (no DTOs, no datos crudos).
    """


    def __init__(self, order, tax_rate:Decimal, shipping_amount:Decimal=0, shipping_taxable:bool=True):
        self.order = order
        self.tax_rate = tax_rate
        self.shipping_amount = shipping_amount
        self.shipping_taxable = shipping_taxable

    
    def calculate_lines_discount(self)->Decimal:
        """Calcula el descuento de variantes/disenos"""
        return sum(line.line_discount for line in self.order.lines)
        
    def calculate_subtotal(self)->Decimal: 
        """Suma subtotales de las líneas."""
    
        return sum(line.subtotal for line in self.order.lines)
    

    def calculate_taxes(self, base:Decimal):
        """Calcula los impuestos de la orden de venta sobre la base imponible"""
        tax_rate = ((self.tax_rate or Decimal('0'))/100)
        if self.shipping_taxable:
            base += self.shipping_amount
        taxes = (base * tax_rate).quantize(CENT)
        return taxes
    
    def calculate_base(self):
        """Calcula la base imponible"""
        subtotal = self.calculate_subtotal()
        discount = self.calculate_order_discount()
        base = (subtotal - discount).quantize(CENT)
        return base


    def calculate_order_discount(self):
        """
        Calcula el descuento aplicado a toda la venta
        """
        subtotal = self.calculate_subtotal()
        discount_rate = self.order.discount_rate/100 or Decimal('0.00')
        discount = (subtotal * discount_rate).quantize(CENT)
        return discount
    
    def calculate_total_discount(self):
        """Calcula el descuento total aplicado a la orden y los descuentos de cada linea"""
        lines_discount = self.calculate_lines_discount()
        order_discount = self.calculate_order_discount()
        return (lines_discount + order_discount).quantize(CENT)

    def calculate_total(self):
        """
        Total = subtotal – descuento + impuestos.
        Devuelve Decimal con 2 decimales, redondeo HALF_UP.
        """
        base = self.calculate_base()
        taxes = self.calculate_taxes(base)
        total = (base + self.shipping_amount + taxes).quantize(CENT)
        return total


    def add_payment(self, amount: Decimal):
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
