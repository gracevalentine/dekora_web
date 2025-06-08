from model.Order import Order
from model.Product import Product

class Transaction:
    def __init__(self, order_id:Order=None, product_id:Product=None, quantity=1, subtotal=0, transaction_id=0):
        self._order_id = order_id
        self._product_id = product_id
        self._quantity = quantity
        self._subtotal = subtotal
        self._transaction_id= transaction_id
    
    @property
    def order_id(self):
        return self._order_id
    
    @order_id.setter
    def order_id(self, value: Order):
        self._order_id = value
        
    @property
    def product_id(self):
        return self._product_id
    
    @product_id.setter
    def product_id(self, value: Product):
        self._product_id = value
    
    @property
    def quantity(self):
        return self._quantity
    
    @quantity.setter
    def quantity(self, value: int):
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        self._quantity = value
    
    @property
    def subtotal(self):
        return self._subtotal
    
    @subtotal.setter
    def subtotal(self, value: float):
        if value < 0:
            raise ValueError("Subtotal cannot be negative")
        self._subtotal = value
    
    @property
    def transaction_id(self):
        return self._transaction_id
    
    @transaction_id.setter
    def transaction_id(self, value: int):
        if value < 0:
            raise ValueError("Transaction ID cannot be negative")
        self._transaction_id = value
        
        