from datetime import datetime
from model.User import User
from model.Product import Product
from model.Cart import Cart

class Order:
    def __init__(self, user_id=User, product_id: Product = None, quantity=1, total_amount=0.0, create_at: datetime = None, cart_id: Cart = None, order_id=0):
        self._user_id = user_id
        self._product_id = product_id
        self._quantity = quantity
        self._order_id = order_id
        self._total_amount = total_amount
        self._create_at = create_at if create_at else datetime.now()
        self._cart_id = cart_id
    
    @property
    def user_id(self):
        return self._user_id
    
    @user_id.setter
    def user_id(self, value: User):
        self._user_id = value
    
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
    def order_id(self):
        return self._order_id
    
    @order_id.setter
    def order_id(self, value: int):
        if value < 0:
            raise ValueError("Order ID cannot be negative")
        self._order_id = value
    
    @property
    def total_amount(self):
        return self._total_amount
    
    @total_amount.setter
    def total_amount(self, value: float):
        if value < 0:
            raise ValueError("Total amount cannot be negative")
        self._total_amount = value
    
    @property
    def create_at(self):
        return self._create_at
    
    @create_at.setter
    def create_at(self, value: datetime):
        if not isinstance(value, datetime):
            raise ValueError("Create at must be a datetime object")
        self._create_at = value
    
    @property
    def cart_id(self):
        return self._cart_id
    
    @cart_id.setter
    def cart_id(self, value: Cart):
        if not isinstance(value, Cart):
            raise ValueError("Cart ID must be a Cart object")
        self._cart_id = value
    
    