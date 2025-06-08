class Product:
    def __init__(self, name='', description='', price=0.0, stock_quantity=0, category="", id=0):
        self._name = name
        self._description = description
        self._price = price
        self._stock_quantity = stock_quantity
        self._category = category
        self._id = id
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value: str):
        if not value:
            raise ValueError("Name cannot be empty")
        self._name = value
        
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value: str):
        if not value:
            raise ValueError("Description cannot be empty")
        self._description = value
    
    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value
    
    @property
    def stock_quantity(self):
        return self._stock_quantity
    
    @stock_quantity.setter
    def stock_quantity(self, value: int):
        if value < 0:
            raise ValueError("Stock quantity cannot be negative")
        self._stock_quantity = value
        
    @property
    def category(self):
        return self._category
    
    @category.setter
    def category(self, value: str):
        if not value:
            raise ValueError("Category cannot be empty")
        self._category = value
    
        