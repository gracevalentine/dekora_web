from model.User import User
from model.Product import Product

class Cart:
    def __init__(self, user_id: User=None, product_id: Product=None, quantity=1, cart_id=0):
        self._user_id = user_id
        self._product_id = product_id
        self._quantity = quantity
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
    def cart_id(self):
        return self._cart_id
    
    @cart_id.setter
    def cart_id(self, value: int):
        if value < 0:
            raise ValueError("Cart ID cannot be negative")
        self._cart_id = value
    