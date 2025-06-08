class User:
    def __init__(self, name='', email='', password='', address='', postal_code='', wallet=0.0, id=0):
        self._name = name
        self._email = email 
        self._password = password
        self._id = id
        self._address = address
        self._postal_code = postal_code
        self._wallet = wallet
