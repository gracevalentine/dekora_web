from datetime import datetime
from model.Order import Order

class Payment:
    def __init__(self, order_id: Order = None, payment_date:datetime = None, payment_id=0):
        self._order_id = order_id
        self._payment_date = payment_date
        self._payment_id = payment_id
    
    @property
    def order_id(self):
        return self._order_id
    
    @order_id.setter
    def order_id(self, value: Order):
        self._order_id = value
    
    @property
    def payment_date(self):
        return self._payment_date
    
    @payment_date.setter
    def payment_date(self, value: datetime):
        if not isinstance(value, datetime):
            raise ValueError("Payment date must be a datetime object")
        self._payment_date = value
    
    @property
    def payment_id(self):
        return self._payment_id
    
    @payment_id.setter
    def payment_id(self, value: int):
        if value < 0:
            raise ValueError("Payment ID cannot be negative")
        self._payment_id = value
    